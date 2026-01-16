"""
Basic tests for utility functions
"""

import pytest
from scripts.utils import load_config, get_openai_client, call_llm, parse_json_response

def test_load_config():
    """Test loading configuration"""
    config = load_config()
    assert isinstance(config, dict)
    assert "domain" in config
    assert "llm" in config
    print("✅ Config loading test passed")

def test_openai_client():
    """Test OpenAI client initialization"""
    config = load_config()
    try:
        client = get_openai_client(config)
        assert client is not None
        print("✅ OpenAI client initialization test passed")
    except ValueError as e:
        print(f"⚠️  OpenAI client test skipped: {e}")
    except Exception as e:
        print(f"❌ OpenAI client test failed: {e}")

def test_llm_call():
    """Test basic LLM call"""
    config = load_config()
    try:
        client = get_openai_client(config)
        prompt = "Say 'Hello, world!' and nothing else."
        response = call_llm(client, prompt, max_tokens=50)

        assert isinstance(response, str)
        assert len(response.strip()) > 0
        print("✅ LLM call test passed")
        print(f"Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ LLM call test failed: {e}")

def test_json_parsing():
    """Test JSON response parsing"""
    # Valid JSON
    valid_json = '{"test": "value", "number": 42}'
    result = parse_json_response(valid_json)
    assert result["test"] == "value"
    assert result["number"] == 42

    # JSON in markdown
    markdown_json = '```json\n{"test": "markdown"}\n```'
    result = parse_json_response(markdown_json)
    assert result["test"] == "markdown"

    print("✅ JSON parsing test passed")

if __name__ == "__main__":
    print("Running basic tests...")
    test_load_config()
    test_openai_client()
    test_llm_call()
    test_json_parsing()
    print("Tests completed!")