#!/usr/bin/env python3
"""
Test LLM calls specifically for the PDF processing workflow
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    extract_text_from_pdf,
    parse_paper_metadata,
    extract_citations_from_text,
    get_openai_client,
    load_config
)

def test_llm_workflow(pdf_path: str):
    """Test the LLM workflow for PDF processing"""

    print(f"Testing LLM workflow with: {pdf_path}")

    # Load config and client
    config = load_config()
    client = get_openai_client(config)
    print("✓ LLM client initialized")

    # Extract text
    text = extract_text_from_pdf(pdf_path)
    print(f"✓ Extracted {len(text):,} characters from PDF")

    # Test metadata parsing
    print("\n--- Testing Metadata Parsing ---")
    metadata = parse_paper_metadata(text, client, config)
    print(f"Title: {metadata.get('title', 'N/A')[:100]}...")
    print(f"Authors: {metadata.get('authors_raw', 'N/A')[:100]}...")
    print(f"ArXiv ID: {metadata.get('arxiv_id', 'N/A')}")

    # Test citation extraction
    print("\n--- Testing Citation Extraction ---")
    citations = extract_citations_from_text(text, client, config)
    print(f"Found {len(citations)} citations")
    if citations:
        print(f"Sample citation: {citations[0].get('title', 'N/A')[:100]}...")

    print("\n✓ LLM workflow test completed successfully!")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test LLM calls for PDF processing')
    parser.add_argument('pdf_path', help='Path to a single PDF file to test')

    args = parser.parse_args()
    test_llm_workflow(args.pdf_path)