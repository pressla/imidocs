import requests
from bs4 import BeautifulSoup
import html2text
import os
from urllib.parse import urlparse
import argparse
import sys
import re
from requests.exceptions import RequestException, Timeout, SSLError


def clean_html(soup):
    """Clean the HTML content by removing unnecessary elements"""
    # Remove navigation elements
    for nav in soup.find_all(["nav", "header", "footer"]):
        nav.decompose()

    # Remove script and style elements
    for element in soup.find_all(["script", "style", "noscript"]):
        element.decompose()

    # Remove comments
    for element in soup.find_all(
        string=lambda text: isinstance(text, str) and ("<!--" in text or "-->" in text)
    ):
        element.extract()

    # Remove specific elements
    unwanted_selectors = [
        ".navigation",
        ".footer",
        ".header",
        ".sidebar",
        ".menu",
        ".nav",
        '[id*="skip"]',
        '[class*="skip"]',  # Skip navigation/contents elements
        ".breadcrumbs",
        ".breadcrumb",
        ".toolbar",
        ".tools",
        "#navigation",
        "#footer",
        "#header",
    ]
    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

    return soup


def format_yaml(content):
    """Format YAML content with proper indentation"""
    lines = content.split("\n")
    formatted_lines = []
    indent = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == "EOF":
            continue

        if stripped.startswith("---"):
            indent = 0
            formatted_lines.append(stripped)
        elif stripped.endswith(":"):
            formatted_lines.append(" " * indent + stripped)
            indent += 2
        else:
            formatted_lines.append(" " * indent + stripped)

    return "\n".join(formatted_lines)


def looks_like_command(line, shell_commands):
    """Check if a line looks like a shell command based on structure"""
    line = line.strip()

    # Skip if line is empty or looks like markdown/formatting
    if not line or line.startswith(("#", ">", "|", "!", "[", "-")):
        return False

    # Skip if line is a description or note
    if any(
        x in line.lower()
        for x in ["requires", "by default", "also", "either", "and source"]
    ):
        return False

    # Check if line starts with a command
    if any(line.startswith(cmd) for cmd in shell_commands):
        return True

    # Check for command with arguments pattern
    if any(f" {cmd} " in f" {line} " for cmd in shell_commands):
        # Additional checks to avoid false positives
        if (
            "|" not in line  # Not a table row
            and not line.endswith(":")  # Not a description
            and not re.match(r"^\d+\.", line)  # Not a numbered step
            and "<" not in line  # Not HTML/XML
            and "=" not in line  # Not a variable assignment
        ):
            return True

    return False


def post_process_markdown(content):
    """Clean up and format the markdown content"""
    lines = content.split("\n")
    processed_lines = []
    current_block = []
    in_code_block = False
    in_table = False
    yaml_block = []
    code_block_type = None
    table_data = []

    # Define shell commands
    shell_commands = [
        "mkdir",
        "systemctl",
        "export",
        "source",
        "echo",
        "curl",
        "cd",
        "git",
        "kubectl",
        "helm",
        "docker",
        "sudo",
        "apt",
        "yum",
        "dnf",
        "rpm",
        "tar",
        "cp",
        "mv",
        "rm",
        "cat",
        "ls",
        "chmod",
        "chown",
        "tee",
        "sh",
        "bash",
    ]

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1

        # Skip unwanted content
        if not line or line == "×" or (not processed_lines and not line.strip()):
            continue

        # Handle code blocks
        if line.strip() == "BASH":
            continue

        # Check if line starts or ends a code block
        if line.strip().startswith("```"):
            if in_code_block:
                processed_lines.append("```")
                processed_lines.append("")
                in_code_block = False
            else:
                code_block_type = line.strip().replace("```", "").lower() or "bash"
                processed_lines.append(f"```{code_block_type}")
                in_code_block = True
            continue

        # Handle YAML content
        if "kind:" in line or "apiVersion:" in line:
            if in_code_block:
                processed_lines.append("```")
                processed_lines.append("")
                in_code_block = False
            yaml_content = [line.strip()]
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line == "EOF":
                    break
                yaml_content.append(next_line)
                i += 1
            processed_lines.append("```yaml")
            processed_lines.append(format_yaml("\n".join(yaml_content)))
            processed_lines.append("```")
            processed_lines.append("")
            continue

        # Handle content within code blocks
        if in_code_block:
            if line.strip():  # Only add non-empty lines
                processed_lines.append(line)
            continue

        # Check if line is a shell command
        if looks_like_command(line, shell_commands):
            processed_lines.append("```bash")
            processed_lines.append(line.strip())
            processed_lines.append("```")
            processed_lines.append("")
            continue

        # Handle tables
        if "|" in line and not line.strip().startswith("!"):
            if not in_table:
                in_table = True
                table_data = []

            # Clean and format table row
            line = line.strip()

            # Skip lines that look like they're part of a code block
            if line.startswith("```") or line == "BASH":
                continue

            # Remove any backticks and formatting from table cells
            line = line.replace("`", "")
            line = line.replace("**", "")
            line = line.replace("--", "")  # Remove dashes that might be part of text
            line = re.sub(r"\s+", " ", line)  # Normalize whitespace

            # Split into cells and clean them
            cells = [cell.strip() for cell in line.split("|")]
            cells = [cell for cell in cells if cell]  # Remove empty cells

            # Skip empty or invalid rows
            if cells and not any(
                x in " ".join(cells).lower() for x in ["important note", "below given"]
            ):
                table_data.append(cells)

        elif in_table:
            in_table = False
            if table_data:
                # Add empty line before table
                processed_lines.append("")

                # Calculate max columns
                max_cols = max(len(row) for row in table_data)

                # Output header row
                header = table_data[0]
                header.extend([""] * (max_cols - len(header)))  # Pad with empty cells
                processed_lines.append("| " + " | ".join(header) + " |")

                # Output separator
                processed_lines.append(
                    "|" + "|".join(" --- " for _ in range(max_cols)) + "|"
                )

                # Output data rows
                for row in table_data[1:]:
                    # Skip empty or separator rows
                    if not row or all(
                        not cell.strip() or cell.strip() == "-" for cell in row
                    ):
                        continue
                    row.extend([""] * (max_cols - len(row)))  # Pad with empty cells
                    processed_lines.append("| " + " | ".join(row) + " |")

                # Add empty line after table
                processed_lines.append("")
            table_data = []
            continue

        # Handle regular content
        else:
            # Fix image links with improved pattern matching
            if line.startswith("!["):
                line = re.sub(r"!\[\]\((\.\.\/)*([^)]+)\)", r"![image](\2)", line)
                line = re.sub(
                    r"!\[image\]\((?!http)([^)]+)\)", r"![image](../\1)", line
                )

            # Handle headers with proper spacing and formatting
            if line.startswith("#") or re.match(r"^Step \d+:", line):
                if processed_lines and processed_lines[-1]:
                    processed_lines.append("")

                # Convert "Step X:" format to proper header
                if re.match(r"^Step \d+:", line):
                    line = "### " + line.replace("\\", "")  # Remove escape characters

            # Clean up numbered steps and descriptions
            if re.match(r"^\d+\\?\.[\s\n]", line):
                line = re.sub(r"^(\d+)\\?\.", r"\1.", line)
            elif line.strip().startswith("\\"):
                line = line.strip().replace("\\", "")

            processed_lines.append(line)

            # Ensure proper spacing around headers
            if line.startswith("#"):
                processed_lines.append("")

    # Handle any remaining code block
    if in_code_block:
        processed_lines.append("```")
        processed_lines.append("")

    # Handle any remaining table
    if in_table and table_data:
        processed_lines.append("")
        max_cols = max(len(row) for row in table_data)
        header = table_data[0]
        header.extend([""] * (max_cols - len(header)))
        processed_lines.append("| " + " | ".join(header) + " |")
        processed_lines.append("|" + "|".join(" --- " for _ in range(max_cols)) + "|")
        for row in table_data[1:]:
            if not row or all(not cell.strip() or cell.strip() == "-" for cell in row):
                continue
            row.extend([""] * (max_cols - len(row)))
            processed_lines.append("| " + " | ".join(row) + " |")
        processed_lines.append("")

    content = "\n".join(processed_lines)

    # Final cleanup
    content = re.sub(r"\n{3,}", "\n\n", content)
    content = re.sub(r"(?m)^\s+$", "", content)

    return content.strip()


def scrape_and_convert(path, verify_ssl=True):
    """
    Scrape a documentation page and convert it to markdown
    """
    try:
        print(f"Reading content from {path}...")

        # Handle both URLs and local files
        if path.startswith(("http://", "https://")):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(
                path, headers=headers, verify=verify_ssl, timeout=30
            )
            response.raise_for_status()
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                return False
            html_content = response.text
        else:
            # Handle local file
            with open(path, "r", encoding="utf-8") as f:
                html_content = f.read()
        print("Content fetched successfully!")

        print("Parsing and cleaning HTML content...")
        soup = BeautifulSoup(html_content, "html.parser")
        cleaned_soup = clean_html(soup)

        # Find the main content area
        main_content = (
            cleaned_soup.find("main")
            or cleaned_soup.find(class_=lambda x: x and "content" in x.lower())
            or cleaned_soup
        )

        print("Converting to markdown...")
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = False
        converter.body_width = 0  # Don't wrap lines
        converter.unicode_snob = True  # Use Unicode characters
        converter.skip_internal_links = True
        converter.inline_links = True
        converter.protect_links = True  # Don't let line wrapping break links

        markdown_content = converter.handle(str(main_content))

        # Post-process the markdown content
        markdown_content = post_process_markdown(markdown_content)

        if not markdown_content.strip():
            print("Error: Generated markdown content is empty!")
            return False

        # Create output directory if it doesn't exist
        os.makedirs("scraped_docs", exist_ok=True)

        # Generate filename from path
        if path.startswith(("http://", "https://")):
            parsed_url = urlparse(path)
            base_name = os.path.basename(parsed_url.path) or "index"
            if not base_name.endswith(".html"):
                base_name = base_name + ".html"
        else:
            base_name = os.path.basename(path)

        print("Saving files...")
        # Save markdown version
        md_path = os.path.join("scraped_docs", base_name.replace(".html", ".md"))
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"\nSuccess! File saved to: {md_path}")
        return True

    except Timeout:
        print(f"Error: Request timed out after 30 seconds")
    except SSLError:
        print(f"Error: SSL Certificate verification failed")
        print("Tip: Try running with --no-verify-ssl if you trust this site")
    except RequestException as e:
        print(f"Error fetching the URL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback

        traceback.print_exc()

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Scrape documentation pages and convert to markdown"
    )
    parser.add_argument("path", help="URL or local path of the HTML file to convert")
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Disable SSL certificate verification (for URLs only)",
    )
    args = parser.parse_args()

    success = scrape_and_convert(args.path, verify_ssl=not args.no_verify_ssl)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
