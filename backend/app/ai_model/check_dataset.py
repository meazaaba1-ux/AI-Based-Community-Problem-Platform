
import csv
from pathlib import Path
from collections import Counter

dataset_path = Path(__file__).parent / "dataset.csv"

# Read the file and ignore empty lines
with dataset_path.open("r", encoding="utf-8-sig") as f:
    lines = [line for line in f if line.strip()]

if not lines:
    raise ValueError("dataset.csv contains no data.")

reader = csv.DictReader(lines)

# Clean the column names
if reader.fieldnames is None:
    raise ValueError("Could not read the CSV column headers.")

reader.fieldnames = [field.strip() for field in reader.fieldnames]

# Check required columns
required_columns = {"description", "category"}

if not required_columns.issubset(reader.fieldnames):
    raise ValueError(
        f"Expected columns {required_columns}, "
        f"but found {reader.fieldnames}"
    )

rows = list(reader)

print("Total reports:", len(rows))
print("\nReports in each category:")

counts = Counter(row["category"].strip() for row in rows)

for category, count in sorted(counts.items()):
    print(f"{category}: {count}")

missing_rows = [
    row for row in rows
    if not row["description"].strip()
    or not row["category"].strip()
]

print("\nRows with missing information:", len(missing_rows))
