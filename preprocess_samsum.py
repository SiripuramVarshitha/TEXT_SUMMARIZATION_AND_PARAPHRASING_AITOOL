import csv
import re

# ---------- 1. Cleaning Function ----------
def clean_text(text):
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces/newlines
    return text

# ---------- 2. Process One File ----------
def process_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["dialogue_clean", "summary_clean"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            dialogue = clean_text(row["dialogue"])
            summary = clean_text(row["summary"])
            writer.writerow({"dialogue_clean": dialogue, "summary_clean": summary})

    print(f"✅ Saved cleaned file: {output_path}")


# ---------- 3. Run on All Splits ----------
process_file("data/samsum-train.csv", "data/train_clean.csv")
process_file("data/samsum-validation.csv", "data/val_clean.csv")
process_file("data/samsum-test.csv", "data/test_clean.csv")
