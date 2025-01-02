#!/usr/bin/env python3
import os
import argparse
from PyPDF2 import PdfReader, PdfWriter


def split_pdf(input_path, pages_per_chunk=10, output_dir="split_pdfs"):
    """
    Split a PDF into smaller chunks with specified number of pages per chunk.

    Args:
        input_path (str): Path to input PDF file
        pages_per_chunk (int): Number of pages per output PDF
        output_dir (str): Directory to store split PDFs
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get PDF name without extension
    pdf_name = os.path.splitext(os.path.basename(input_path))[0]

    # Read the PDF
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    # Calculate number of chunks
    num_chunks = (total_pages + pages_per_chunk - 1) // pages_per_chunk

    print(f"Total pages: {total_pages}")
    print(f"Pages per chunk: {pages_per_chunk}")
    print(f"Number of chunks: {num_chunks}")

    # Split the PDF into chunks
    for chunk in range(num_chunks):
        writer = PdfWriter()

        # Calculate start and end pages for this chunk
        start_page = chunk * pages_per_chunk
        end_page = min(start_page + pages_per_chunk, total_pages)

        # Add pages to writer
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        # Generate output filename
        output_filename = f"{pdf_name}_part{chunk+1}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        # Write the chunk to a file
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        print(f"Created: {output_filename} (Pages {start_page + 1}-{end_page})")


def main():
    parser = argparse.ArgumentParser(description="Split PDF into smaller chunks")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument(
        "--pages", type=int, default=10, help="Number of pages per chunk (default: 10)"
    )
    parser.add_argument(
        "--output-dir",
        default="split_pdfs",
        help="Output directory (default: split_pdfs)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file '{args.input_pdf}' does not exist")
        return

    split_pdf(args.input_pdf, args.pages, args.output_dir)


if __name__ == "__main__":
    main()
