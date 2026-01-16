"""
CSV validation and schema checking utilities
"""

import pandas as pd
import os
from typing import Dict, List, Tuple

# Expected CSV schemas
SCHEMAS = {
    "keywords_expanded.csv": ["original", "expanded", "category"],
    "papers.csv": ["arxiv_id", "title", "authors_raw", "affiliations", "summary", "published_date", "url", "categories"],
    "researchers.csv": ["name", "affiliation", "research_focus", "seniority", "papers"],
    "researchers_enriched.csv": ["name", "affiliation", "research_focus", "seniority", "papers", "linkedin", "twitter", "github"],
    "researchers_outreach.csv": ["name", "affiliation", "research_focus", "seniority", "papers", "linkedin", "twitter", "github", "personalized_message", "status", "sent_date", "notes"]
}

def validate_csv_schema(filepath: str) -> Tuple[bool, str]:
    """
    Validate that CSV has expected columns
    Returns (is_valid, error_message)
    """
    if not os.path.exists(filepath):
        return False, f"File does not exist: {filepath}"

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return False, f"Could not read CSV: {str(e)}"

    filename = os.path.basename(filepath)
    if filename not in SCHEMAS:
        return False, f"No schema defined for {filename}"

    expected_cols = set(SCHEMAS[filename])
    actual_cols = set(df.columns)

    if expected_cols != actual_cols:
        missing = expected_cols - actual_cols
        extra = actual_cols - expected_cols

        error_msg = f"Schema mismatch for {filename}:"
        if missing:
            error_msg += f"\n  Missing columns: {sorted(missing)}"
        if extra:
            error_msg += f"\n  Extra columns: {sorted(extra)}"

        return False, error_msg

    return True, "Schema valid"

def validate_csv_data(filepath: str) -> List[str]:
    """Validate data quality in CSV"""
    issues = []

    if not os.path.exists(filepath):
        return [f"File does not exist: {filepath}"]

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return [f"Could not read CSV: {str(e)}"]

    filename = os.path.basename(filepath)

    # Check for empty DataFrame
    if df.empty:
        issues.append("CSV is empty")

    # Check for null values in critical columns
    if filename == "researchers.csv":
        critical_cols = ["name"]
    elif filename == "papers.csv":
        critical_cols = ["arxiv_id", "title"]
    else:
        critical_cols = []

    for col in critical_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                issues.append(f"{null_count} null values in critical column '{col}'")

    # Check for duplicates
    if filename == "researchers.csv" and "name" in df.columns:
        dup_count = df["name"].duplicated().sum()
        if dup_count > 0:
            issues.append(f"{dup_count} duplicate researcher names")

    return issues

def validate_all_csvs(data_dir: str = "data/") -> Dict[str, Dict]:
    """Validate all expected CSV files"""
    results = {}

    for filename in SCHEMAS.keys():
        filepath = os.path.join(data_dir, filename)
        schema_valid, schema_msg = validate_csv_schema(filepath)
        data_issues = validate_csv_data(filepath)

        results[filename] = {
            "exists": os.path.exists(filepath),
            "schema_valid": schema_valid,
            "schema_message": schema_msg,
            "data_issues": data_issues
        }

    return results

def print_validation_report(results: Dict[str, Dict]):
    """Print human-readable validation report"""
    print("CSV Validation Report")
    print("=" * 50)

    for filename, result in results.items():
        print(f"\n{filename}:")
        if not result["exists"]:
            print("  ❌ File does not exist")
            continue

        if result["schema_valid"]:
            print("  ✅ Schema valid")
        else:
            print("  ❌ Schema invalid:")
            print(f"     {result['schema_message']}")

        if result["data_issues"]:
            print("  ⚠️  Data issues:")
            for issue in result["data_issues"]:
                print(f"     - {issue}")
        else:
            print("  ✅ No data issues found")

if __name__ == "__main__":
    results = validate_all_csvs()
    print_validation_report(results)