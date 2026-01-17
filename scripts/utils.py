"""
Shared utilities for the Contact Scholar pipeline
"""

import os
import yaml
import json
import time
import re
from typing import Dict, Any, Optional, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF processing

# Load environment variables
load_dotenv()

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from YAML file

    Priority order:
    1. Specified config_path
    2. config/custom.yaml (user's custom config)
    3. config/default.yaml (template)
    """
    if config_path is None:
        # Get the project root directory (parent of scripts directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)

        # Try custom config first, then default
        candidates = [
            os.path.join(project_root, "config", "custom.yaml"),
            os.path.join(project_root, "config", "default.yaml")
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                config_path = candidate
                break
        else:
            raise FileNotFoundError(f"No config file found. Looked for: {candidates}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_openai_client(config: Dict[str, Any] = None) -> OpenAI:
    """Initialize OpenAI client for OpenRouter"""
    if config is None:
        config = load_config()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    return OpenAI(
        api_key=api_key,
        base_url=config['llm']['base_url']
    )

def call_llm(
    client: OpenAI,
    prompt: str,
    model: str = "deepseek/deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    max_retries: int = 3
) -> str:
    """Make LLM call with retry logic"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"LLM call failed (attempt {attempt + 1}), retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff

def load_prompt_template(template_name: str) -> str:
    """Load prompt template"""
    # Get the project root directory (parent of scripts directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    template_path = os.path.join(project_root, "config", "prompts", f"{template_name}.txt")

    with open(template_path, 'r') as f:
        template = f.read()

    return template

def parse_json_response(response: str, max_retries: int = 3) -> Dict[str, Any]:
    """Parse JSON response with error handling and repair attempts"""
    # First try direct parsing
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # If that fails, try to extract JSON from markdown code blocks
    import re
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # If still failing, try to repair common JSON issues
    for attempt in range(max_retries):
        try:
            # Try to fix common issues
            repaired = response.strip()
            # Remove markdown formatting
            repaired = re.sub(r'```\w*\n?', '', repaired)
            repaired = re.sub(r'```\n?', '', repaired)
            # Fix trailing commas
            repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)

            return json.loads(repaired)
        except json.JSONDecodeError:
            continue

    raise ValueError(f"Could not parse JSON response after {max_retries} repair attempts")

def ensure_data_dir(data_dir: str = "data/"):
    """Ensure data directory exists"""
    # Get the project root directory (parent of scripts directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    full_data_dir = os.path.join(project_root, data_dir)
    os.makedirs(full_data_dir, exist_ok=True)
    return full_data_dir

def save_csv_checkpoint(df, filename: str, data_dir: str = "data/"):
    """Save DataFrame as CSV checkpoint"""
    full_data_dir = ensure_data_dir(data_dir)
    filepath = os.path.join(full_data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved checkpoint: {filepath}")

def load_csv_checkpoint(filename: str, data_dir: str = "data/"):
    """Load DataFrame from CSV checkpoint"""
    import pandas as pd
    # Get the project root directory (parent of scripts directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    filepath = os.path.join(project_root, data_dir, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return None

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def extract_arxiv_id_from_text(text: str) -> Optional[str]:
    """Extract arXiv ID from PDF text content"""
    # Look for arXiv ID patterns like arXiv:1234.56789v1 or 1234.56789
    patterns = [
        r'arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)',  # arXiv:1234.56789v1
        r'arXiv\s*id\s*:?\s*(\d{4}\.\d{4,5}(?:v\d+)?)',  # arXiv id: 1234.56789
        r'(\d{4}\.\d{4,5}(?:v\d+)?)',  # Just the ID: 1234.56789v1
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            arxiv_id = match.group(1) if match.lastindex == 1 else match.group(1)
            # Ensure it has the arXiv: prefix for consistency
            if not arxiv_id.startswith('arXiv:'):
                arxiv_id = f'arXiv:{arxiv_id}'
            return arxiv_id

    return None

def extract_arxiv_id_from_filename(filename: str) -> Optional[str]:
    """Extract arXiv ID from filename if present"""
    # Look for patterns like 1234.56789.pdf or arXiv-1234.56789.pdf
    patterns = [
        r'arXiv[_\-](\d{4}\.\d{4,5}(?:v\d+)?)',  # arXiv-1234.56789
        r'(\d{4}\.\d{4,5}(?:v\d+)?)\.pdf',  # 1234.56789.pdf
    ]

    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            arxiv_id = match.group(1)
            if not arxiv_id.startswith('arXiv:'):
                arxiv_id = f'arXiv:{arxiv_id}'
            return arxiv_id

    return None

def parse_paper_metadata(text: str, client: OpenAI, config: Dict[str, Any]) -> Dict[str, Any]:
    """Parse paper metadata from PDF text using LLM"""
    # Create a prompt for metadata extraction
    prompt = f"""Extract the following metadata from this academic paper text:

{text[:8000]}  # Limit text to avoid token limits

Return as JSON:
{{
  "title": "Full paper title",
  "authors": "Author names separated by | ",
  "abstract": "Paper abstract/summary",
  "arxiv_id": "arXiv ID if found (format: XXXX.XXXXX)",
  "published_date": "Publication date if available (YYYY-MM-DD format)"
}}

If any field is not found, use empty string or "Unknown".
"""

    try:
        response = call_llm(
            client=client,
            prompt=prompt,
            model=config['llm']['model'],
            temperature=0.1,  # Low temperature for extraction
            max_tokens=1000
        )

        data = parse_json_response(response)
        return {
            'title': data.get('title', ''),
            'authors_raw': data.get('authors', ''),
            'summary': data.get('abstract', ''),
            'arxiv_id': data.get('arxiv_id', ''),
            'published_date': data.get('published_date', 'Unknown')
        }
    except Exception as e:
        print(f"Error parsing metadata: {e}")
        return {
            'title': '',
            'authors_raw': '',
            'summary': '',
            'arxiv_id': '',
            'published_date': 'Unknown'
        }

def extract_citations_from_text(text: str, client: OpenAI, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract citations/references from PDF text using LLM"""
    # Find the references section
    references_section = extract_references_section(text)

    if not references_section:
        return []

    # Use LLM to parse the references into structured format
    prompt = f"""Extract citation information from this references section of an academic paper:

{references_section[:12000]}  # Limit to avoid token limits

For each reference, extract:
- Title of the cited paper
- Authors of the cited paper
- Any arXiv ID or DOI if present
- Publication year if available

Return as JSON array:
[
  {{
    "title": "Title of cited paper",
    "authors": "Author names separated by | ",
    "arxiv_id": "arXiv ID if found",
    "year": "Publication year"
  }}
]

Only include academic paper citations, skip books, websites, etc. If information is missing, use empty strings.
"""

    try:
        response = call_llm(
            client=client,
            prompt=prompt,
            model=config['llm']['model'],
            temperature=0.1,
            max_tokens=2000
        )

        citations = parse_json_response(response)
        if isinstance(citations, list):
            return citations
        return []
    except Exception as e:
        print(f"Error extracting citations: {e}")
        return []

def extract_references_section(text: str) -> str:
    """Extract the references/bibliography section from PDF text"""
    # Common section headers for references
    patterns = [
        r'References?\n(.*?)(?:\n\n[A-Z][a-z]|$)',  # References\n... until next section
        r'Bibliography\n(.*?)(?:\n\n[A-Z][a-z]|$)',  # Bibliography\n...
        r'\nReferences?\s*\n(.*?)(?:\n[A-Z]|\Z)',  # References with spacing
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If no clear section found, look for lines that look like citations
    # This is a fallback for PDFs where section headers aren't clear
    lines = text.split('\n')
    citation_lines = []

    for i, line in enumerate(lines):
        # Look for lines that start with [number] or have citation-like patterns
        if re.match(r'^\[\d+\]', line.strip()) or re.search(r'\d{4}\.', line):
            # Collect this line and a few following lines
            citation_text = line
            for j in range(1, min(5, len(lines) - i)):  # Next 5 lines max
                next_line = lines[i + j]
                if next_line.strip() and not re.match(r'^[A-Z]', next_line.strip()):  # Not a new section
                    citation_text += ' ' + next_line.strip()
                else:
                    break
            citation_lines.append(citation_text)

    if citation_lines:
        return '\n'.join(citation_lines[:50])  # Limit to first 50 citations

    return ""