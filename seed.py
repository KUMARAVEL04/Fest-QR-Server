# seed.py
import sqlite3
import sys

DB_FILE = "people.db"  # same DB file used by backend

def seed_roll_numbers(roll_tuples):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executemany("""
        INSERT OR IGNORE INTO people (roll_number, inside, name) VALUES (?, 0, ?)
    """, roll_tuples)
    conn.commit()
    conn.close()
    print(f"✅ Added {len(roll_tuples)} roll numbers (duplicates ignored).")

def main():
    print("=== Roll Number Bulk Seeder ===")
    print("Paste roll numbers (one per line). Accepts:")
    print("  - ROLL")
    print("  - ROLL,Name")
    print("Type 'done' on a new line when finished:\n")

    roll_tuples = []
    for line in sys.stdin:
        roll = line.strip()
        if roll.lower() == "done":
            break
        if not roll:
            continue
        # parse optional name
        if ',' in roll:
            parts = roll.split(',', 1)
            r = parts[0].strip()
            name = parts[1].strip() or None
        else:
            r = roll
            name = None
        roll_tuples.append((r, name))

    if roll_tuples:
        seed_roll_numbers(roll_tuples)
    else:
        print("⚠️ No roll numbers entered.")

if __name__ == "__main__":
    main()
