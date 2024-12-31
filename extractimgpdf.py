import os
import sys
import fitz  # PyMuPDF


def extract_images_from_pdf(
    pdf_path: str, output_folder: str, min_size: int = 100
) -> list[str]:
    """
    Extract embedded images from PDF and save them.

    Args:
        pdf_path: Path to the PDF file
        output_folder: Directory where images will be saved

    Returns:
        list[str]: List of paths to saved image files
    """
    try:
        # Verify PDF exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Create output directory
        os.makedirs(output_folder, exist_ok=True)

        # Create output directory
        os.makedirs(output_folder, exist_ok=True)

        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        image_paths = []
        image_count = 0

        # Extract images from each page
        for page_num, page in enumerate(doc, 1):
            image_list = page.get_images()

            for img_index, img in enumerate(image_list, 1):
                try:
                    # Get image data
                    xref = img[0]
                    base_image = doc.extract_image(xref)

                    # Skip small images (likely icons or decorative elements)
                    if img[2] < min_size or img[3] < min_size:
                        continue

                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # Save image
                    image_count += 1
                    image_path = os.path.join(
                        output_folder, f"image_{image_count}.{image_ext}"
                    )

                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    image_paths.append(image_path)
                    print(
                        f"Extracted image {image_count} from page {page_num}: {image_path}"
                    )

                except Exception as e:
                    print(
                        f"Failed to extract image {img_index} from page {page_num}: {str(e)}"
                    )
                    continue

        if not image_paths:
            print("Warning: No embedded images found in the PDF")

        return image_paths

    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    finally:
        if "doc" in locals():
            doc.close()


if __name__ == "__main__":
    # Paths and setup
    pdf_path = "docs/kube-patterns-rh.pdf"
    output_folder = "docs/img"

    # Extract images
    # Extract images (minimum 100x100 pixels)
    image_paths = extract_images_from_pdf(pdf_path, output_folder, min_size=100)

    # Print results
    if image_paths:
        print(f"\nSuccessfully extracted {len(image_paths)} images:")
        for path in image_paths:
            print(f"- {path}")
    else:
        print("\nNo images were extracted")
        sys.exit(1)
