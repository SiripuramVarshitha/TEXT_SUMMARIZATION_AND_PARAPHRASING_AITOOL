import csv

# ---------- 1. Show a few sample rows ----------
def show_samples(file_path, n=3):
    print(f"\n📄 Showing {n} samples from {file_path}:\n")
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            print("Dialogue:", row["dialogue_clean"])
            print("Summary :", row["summary_clean"])
            print("-----")
            if i == n-1:
                break

# ---------- 2. Count rows ----------
def count_rows(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return len(rows) - 1   # minus header row

# ---------- 3. Check average lengths ----------
def check_lengths(file_path):
    dialogue_lengths, summary_lengths = [], []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dialogue_lengths.append(len(row["dialogue_clean"].split()))
            summary_lengths.append(len(row["summary_clean"].split()))
    avg_dialogue = sum(dialogue_lengths) / len(dialogue_lengths)
    avg_summary = sum(summary_lengths) / len(summary_lengths)
    return avg_dialogue, avg_summary

# ---------- Run checks ----------
for split in ["train_clean.csv", "val_clean.csv", "test_clean.csv"]:
    file_path = f"data/{split}"
    show_samples(file_path, n=2)
    print(f"Total rows in {split}: {count_rows(file_path)}")
    avg_d, avg_s = check_lengths(file_path)
    print(f"Avg dialogue length: {avg_d:.1f} words | Avg summary length: {avg_s:.1f} words")
    print("="*50)
