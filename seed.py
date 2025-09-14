import sqlite3
import sys

DB_FILE = "people.db"  # same DB file used by backend

def seed_roll_numbers(roll_numbers):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executemany("""
        INSERT OR IGNORE INTO people (roll_number, inside) VALUES (?, 0)
    """, [(roll,) for roll in roll_numbers])
    conn.commit()
    conn.close()
    print(f"✅ Added {len(roll_numbers)} roll numbers (duplicates ignored).")

def main():
    print("=== Roll Number Bulk Seeder ===")
    print("Paste roll numbers (one per line). Type 'done' on a new line when finished:\n")

    roll_numbers = []
    for line in sys.stdin:
        roll = line.strip()
        if roll.lower() == "done":
            break
        if roll:
            roll_numbers.append(roll)

    if roll_numbers:
        seed_roll_numbers(roll_numbers)
    else:
        print("⚠️ No roll numbers entered.")

if __name__ == "__main__":
    main()
