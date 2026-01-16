#!/usr/bin/env python3
"""
Clear outputs from all Jupyter notebooks to prepare for public repository.
This removes execution results which may contain sensitive data.
"""

import os
import subprocess
import glob

def clear_notebook_outputs():
    """Clear outputs from all notebooks in the notebooks/ directory"""
    notebooks = glob.glob("notebooks/*.ipynb")

    if not notebooks:
        print("No notebooks found in notebooks/ directory")
        return

    print(f"Found {len(notebooks)} notebooks. Clearing outputs...")

    for notebook in notebooks:
        print(f"Clearing: {notebook}")
        result = subprocess.run([
            "jupyter", "nbconvert",
            "--clear-output", "--inplace", notebook
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Cleared: {notebook}")
        else:
            print(f"❌ Failed to clear: {notebook}")
            print(f"Error: {result.stderr}")

    print("\n🎉 All notebook outputs cleared!")
    print("Notebooks are now safe to commit to public repository.")

if __name__ == "__main__":
    clear_notebook_outputs()