#!/usr/bin/env python3
"""
Test script to verify the Contact Scholar environment is set up correctly.
Run this before starting the notebooks.
"""

import sys
import os

def test_environment():
    print("🧪 Testing Contact Scholar Environment")
    print("=" * 50)

    # Test 1: Virtual environment
    print("\n1. Testing virtual environment...")
    python_path = sys.executable
    if ".venv" in python_path:
        print("✅ Virtual environment active")
    else:
        print("❌ Not running in virtual environment")
        return False

    # Test 2: Package imports
    print("\n2. Testing package imports...")

    # Add virtual environment packages to path
    import os
    venv_packages = os.path.join(os.path.dirname(__file__), ".venv", "lib", "python3.12", "site-packages")
    if venv_packages not in sys.path:
        sys.path.insert(0, venv_packages)

    packages = [
        ("yaml", "PyYAML"),
        ("openai", "OpenAI"),
        ("pandas", "Pandas"),
        ("dotenv", "python-dotenv"),
        ("tqdm", "tqdm")
    ]

    all_packages_ok = True
    for import_name, display_name in packages:
        try:
            __import__(import_name)
            print(f"✅ {display_name} available")
        except ImportError:
            print(f"❌ {display_name} missing")
            all_packages_ok = False

    if not all_packages_ok:
        print("\n❌ Some packages are missing. Run: uv sync")
        return False

    # Test 3: Config files
    print("\n3. Testing configuration files...")

    config_candidates = ["config/custom.yaml", "config/default.yaml"]
    config_found = False

    for config_path in config_candidates:
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                print(f"✅ Config loaded from {config_path}")
                print(f"   Domain: {config['domain']['name']}")
                print(f"   Keywords: {len(config['keywords'])}")
                config_found = True
                break
            except Exception as e:
                print(f"❌ Error loading {config_path}: {e}")

    if not config_found:
        print("❌ No valid config file found")
        return False

    # Test 4: Environment variables
    print("\n4. Testing environment variables...")

    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key and len(api_key.strip()) > 10:  # Basic validation
        print("✅ OPENROUTER_API_KEY is set")
    else:
        print("❌ OPENROUTER_API_KEY not set or too short")
        print("   Add your OpenRouter API key to .env file")
        return False

    # Test 5: Scripts
    print("\n5. Testing utility scripts...")

    try:
        sys.path.append('scripts')
        from utils import load_config, get_openai_client

        # Test config loading
        config = load_config()
        print("✅ Config loading function works")

        # Test OpenAI client (without making API call)
        try:
            client = get_openai_client()
            print("✅ OpenAI client initialization works")
        except Exception as e:
            print(f"❌ OpenAI client error: {e}")
            return False

    except ImportError as e:
        print(f"❌ Script import error: {e}")
        return False

    print("\n🎉 All tests passed! Environment is ready.")
    print("\nYou can now run the notebooks:")
    print("jupyter notebook notebooks/01_keyword_expansion.ipynb")

    return True

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)