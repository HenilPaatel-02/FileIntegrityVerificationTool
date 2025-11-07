import os
import hashlib
import json
from datetime import datetime
import matplotlib.pyplot as plt

def calculate_hashes(file_path):
    hashes = {"MD5": hashlib.md5(), "SHA1": hashlib.sha1(), "SHA256": hashlib.sha256()}
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            for h in hashes.values():
                h.update(chunk)
    return {name: h.hexdigest() for name, h in hashes.items()}

def scan_directory(directory):
    file_data = {}
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            file_data[full_path] = calculate_hashes(full_path)
    return file_data

def save_baseline_report(data, file_name="baseline_report.json"):
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": data
    }
    with open(file_name, "w") as f:
        json.dump(report, f, indent=4)
    print(f"✅ Baseline report saved as {file_name}")

def verify_integrity(directory, baseline_file="baseline_report.json"):
    with open(baseline_file, "r") as f:
        baseline = json.load(f)["files"]
    current = scan_directory(directory)
    modified, deleted, added = [], [], []

    # Detect modified or deleted
    for path, hashes in baseline.items():
        if path not in current:
            deleted.append(path)
        elif current[path]["SHA256"] != hashes["SHA256"]:
            modified.append(path)

    # Detect newly added
    for path in current:
        if path not in baseline:
            added.append(path)

    return modified, deleted, added

def generate_report(modified, deleted, added):
    total_files = len(modified) + len(deleted) + len(added)
    safe = max(1, 100 - total_files)  # Avoid division by zero
    plt.pie([safe, len(modified), len(deleted), len(added)],
            labels=['Safe', 'Modified', 'Deleted', 'Added'],
            autopct='%1.1f%%', startangle=140)
    plt.title('File Integrity Status')
    plt.savefig("integrity_summary.png")
    print("📊 Integrity summary saved as integrity_summary.png")

if __name__ == "__main__":
    print("\n🧠 File Integrity Verification Tool")
    print("1️⃣ Create baseline\n2️⃣ Verify integrity\n")
    choice = input("Enter your choice (1/2): ")

    folder = input("Enter the folder path: ")
    if choice == "1":
        data = scan_directory(folder)
        save_baseline_report(data)
    elif choice == "2":
        modified, deleted, added = verify_integrity(folder)
        print(f"\n🔍 Modified: {len(modified)} | Deleted: {len(deleted)} | Added: {len(added)}")
        generate_report(modified, deleted, added)
    else:
        print("❌ Invalid choice.")
