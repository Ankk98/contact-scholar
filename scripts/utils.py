"""
Shared utilities for the Contact Scholar pipeline
"""

import os
import yaml
import json
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

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
        # Try custom config first, then default
        candidates = ["config/custom.yaml", "config/default.yaml"]
        for candidate in candidates:
            if os.path.exists(candidate):
                config_path = candidate
                break
        else:
            raise FileNotFoundError("No config file found. Please create config/default.yaml or config/custom.yaml")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_openai_client() -> OpenAI:
    """Initialize OpenAI client for OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
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

def load_prompt_template(template_name: str, **kwargs) -> str:
    """Load and format prompt template"""
    template_path = f"config/prompts/{template_name}.txt"

    with open(template_path, 'r') as f:
        template = f.read()

    return template.format(**kwargs)

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
    os.makedirs(data_dir, exist_ok=True)

def save_csv_checkpoint(df, filename: str, data_dir: str = "data/"):
    """Save DataFrame as CSV checkpoint"""
    ensure_data_dir(data_dir)
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved checkpoint: {filepath}")

def load_csv_checkpoint(filename: str, data_dir: str = "data/"):
    """Load DataFrame from CSV checkpoint"""
    import pandas as pd
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return None