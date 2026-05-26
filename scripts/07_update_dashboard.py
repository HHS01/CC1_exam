"""
07_update_dashboard.py
======================
Updates the dashboard HTML files (index.html) to reflect the target country.
Performs surgical string replacements for titles, headers, and data paths.

Inputs: PIPELINE_ISO3, PIPELINE_COUNTRY
"""

import os
import re
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3    = os.environ.get("PIPELINE_ISO3", "BFA")
COUNTRY = os.environ.get("PIPELINE_COUNTRY", "Burkina Faso")

def update_file(file_path: Path, patterns: list):
    if not file_path.exists():
        print(f"  ⚠ File not found: {file_path}")
        return

    print(f"  Updating {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, new_content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✓ Updated {file_path}")
    else:
        print(f"  - No changes needed for {file_path}")

def main():
    print(f"🚀 Updating dashboard for {ISO3} ({COUNTRY})...")

    # 1. Main Index
    main_index = Path("index.html")
    main_patterns = [
        (r"Burkina Faso · Structural & Conflict Risk · 2015–2026", f"{COUNTRY} · Structural & Conflict Risk · 2015–2026"),
        (r"Province: \${name}, Burkina Faso", f"Province: ${{name}}, {COUNTRY}"),
        # If there are other hardcoded strings, add them here
    ]
    update_file(main_index, main_patterns)

    # 2. Schools Index
    schools_index = Path("schools/index.html")
    schools_patterns = [
        (r"Burkina Faso · Education Infrastructure · 2015–2026", f"{COUNTRY} · Education Infrastructure · 2015–2026"),
        (r"analysis of Burkina Faso schools", f"analysis of {COUNTRY} schools"),
        (r"BFA_school_vulnerability.csv", f"{ISO3}_school_vulnerability.csv"),
        # Center map logic could be added here if we had country centroids
    ]
    update_file(schools_index, schools_patterns)

    # 3. At Risk Summary
    summary_index = Path("schools/at_risk_summary.html")
    summary_patterns = [
        (r"BFA_school_vulnerability.csv", f"{ISO3}_school_vulnerability.csv"),
    ]
    update_file(summary_index, summary_patterns)

    print("✅ Dashboard update complete.")

if __name__ == "__main__":
    main()
