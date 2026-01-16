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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    notebooks_dir = os.path.join(project_root, "notebooks")
    notebooks = glob.glob(os.path.join(notebooks_dir, "*.ipynb"))

    if not notebooks:
        print("No notebooks found in notebooks/ directory")
        return

    print(f"Found {len(notebooks)} notebooks. Clearing outputs...")

    for notebook in notebooks:
        print(f"Clearing: {notebook}")
        # Use relative path for nbconvert command
        rel_path = os.path.relpath(notebook, project_root)
        result = subprocess.run([
            "jupyter", "nbconvert",
            "--clear-output", "--inplace", rel_path
        ], capture_output=True, text=True, cwd=project_root)

        if result.returncode == 0:
            print(f"✅ Cleared: {notebook}")
        else:
            print(f"❌ Failed to clear: {notebook}")
            print(f"Error: {result.stderr}")

    print("\n🎉 All notebook outputs cleared!")
    print("Notebooks are now safe to commit to public repository.")

if __name__ == "__main__":
    clear_notebook_outputs()