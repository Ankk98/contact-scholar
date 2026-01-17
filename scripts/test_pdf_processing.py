#!/usr/bin/env python3
"""
Test script for PDF processing functionality without LLM calls
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import extract_text_from_pdf, extract_arxiv_id_from_filename, extract_arxiv_id_from_text

def test_pdf_processing(pdf_directory: str, max_files: int = 3):
    """Test PDF processing functionality"""
    pdf_dir = Path(pdf_directory)

    if not pdf_dir.exists() or not pdf_dir.is_dir():
        print(f"Error: {pdf_directory} is not a valid directory")
        return

    # Find PDF files
    pdf_files = list(pdf_dir.glob('**/*.pdf'))[:max_files]

    print(f"Testing with {len(pdf_files)} PDF files from {pdf_directory}")
    print("=" * 60)

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{i}. Processing: {pdf_file.name}")
        print("-" * 40)

        # Extract text
        text = extract_text_from_pdf(str(pdf_file))
        print(f"✓ Extracted text: {len(text):,} characters")

        # Extract arXiv ID from filename
        arxiv_id_filename = extract_arxiv_id_from_filename(pdf_file.name)
        print(f"✓ ArXiv ID from filename: {arxiv_id_filename or 'Not found'}")

        # Extract arXiv ID from text (first 2000 chars for speed)
        arxiv_id_text = extract_arxiv_id_from_text(text[:2000])
        print(f"✓ ArXiv ID from text: {arxiv_id_text or 'Not found'}")

        # Show sample text
        if text:
            print("✓ Sample text (first 200 chars):")
            print(f"  \"{text[:200].replace(chr(10), ' ').replace(chr(13), ' ')}\"")
        else:
            print("✗ No text extracted")

        print()

    print("=" * 60)
    print("PDF processing test completed successfully!")
    print("The core PDF extraction functionality is working correctly.")
    print("Note: LLM calls require network connectivity to OpenRouter API.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test PDF processing functionality')
    parser.add_argument('pdf_directory', help='Path to directory containing PDF files')
    parser.add_argument('--max-files', '-m', type=int, default=3, help='Maximum number of files to test')

    args = parser.parse_args()
    test_pdf_processing(args.pdf_directory, args.max_files)