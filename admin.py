# admin.py
import sqlite3
from datetime import datetime
import os

DB_FILE = "people.db"
LOG_FILE = "changes.log"
DUMMY_FILE = "dummy_rolls.txt"

def write_log(entry_line):
    ts = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} {entry_line}\n")

def show_inside(cursor):
    cursor.execute("SELECT COUNT(*) FROM people WHERE inside=1")
    (count,) = cursor.fetchone()

    cursor.execute("SELECT roll_number, name FROM people WHERE inside=1")
    rows = cursor.fetchall()

    print(f"\nPeople inside: {count}")
    if count > 0:
        print("Roll numbers (roll | name):")
        for roll, name in rows:
            print(" -", roll, "|", name if name else "-")

def show_all(cursor):
    cursor.execute("SELECT roll_number, inside, name FROM people ORDER BY roll_number")
    rows = cursor.fetchall()

    print("\nDatabase (roll_number | status | name):")
    for roll, inside, name in rows:
        status = "Inside" if inside == 1 else "Outside"
        print(f"{roll} | {status} | {name if name else '-'}")

def search_roll(cursor, roll_number):
    cursor.execute("SELECT inside, name FROM people WHERE roll_number=?", (roll_number,))
    row = cursor.fetchone()
    if row is None:
        print(f"\nRoll number {roll_number} not found in database.")
    else:
        status = "Inside" if row[0] == 1 else "Outside"
        print(f"\n{roll_number} is currently: {status} (name: {row[1] if row[1] else '-'})")

def load_dummy_list():
    if not os.path.exists(DUMMY_FILE):
        return []
    with open(DUMMY_FILE, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return items

def save_dummy_list(items):
    with open(DUMMY_FILE, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item + "\n")

def add_roll(cursor, conn, roll, name=None):
    """
    Adds a new roll number. The new roll is Outside (inside=0) by default.
    """
    cursor.execute("SELECT 1 FROM people WHERE roll_number=?", (roll,))
    if cursor.fetchone():
        print(f"Roll {roll} already exists. Skipping insert.")
        return False
    cursor.execute("INSERT INTO people (roll_number, inside, name) VALUES (?, 0, ?)", (roll, name))
    conn.commit()
    write_log(f"ADD roll={roll!r} name={name!r}")
    print(f"Added roll {roll} (name: {name}). Default status: Outside.")
    return True

def replace_roll(cursor, conn, old_roll, new_roll, new_name=None, remove_dummy_from_file=False):
    cursor.execute("SELECT inside, name FROM people WHERE roll_number=?", (old_roll,))
    row = cursor.fetchone()
    if row is None:
        print(f"Old roll {old_roll} not found.")
        return False
    cursor.execute("SELECT 1 FROM people WHERE roll_number=?", (new_roll,))
    if cursor.fetchone():
        print(f"New roll {new_roll} already exists in DB. Choose a different new roll.")
        return False

    old_inside, old_name = row
    # perform update of primary key (keeps inside as it was)
    try:
        cursor.execute("UPDATE people SET roll_number=?, name=? WHERE roll_number=?", (new_roll, new_name if new_name is not None else old_name, old_roll))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print("Failed to replace (integrity error):", e)
        return False

    write_log(f"REPLACE old_roll={old_roll!r} new_roll={new_roll!r} old_name={old_name!r} new_name={(new_name if new_name is not None else old_name)!r} inside={old_inside}")
    print(f"Replaced {old_roll} → {new_roll} (name now: {new_name if new_name is not None else old_name}).")

    if remove_dummy_from_file:
        items = load_dummy_list()
        if new_roll in items:
            items = [it for it in items if it != new_roll]
            save_dummy_list(items)
            print(f"Removed {new_roll} from {DUMMY_FILE}.")
    return True

def reset_everyone_outside(cursor, conn):
    """
    Sets inside=0 for all rows (everyone is Outside).
    Returns number of rows changed.
    """
    cursor.execute("UPDATE people SET inside=0 WHERE inside!=0")
    changed = cursor.rowcount if cursor.rowcount is not None else 0
    conn.commit()
    write_log(f"RESET_ALL set all to outside (changed_rows={changed})")
    print(f"Reset completed. Rows changed: {changed}")
    return changed

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    while True:
        print("\n--- MENU ---")
        print("1. Show count and list of people inside")
        print("2. Show entire database")
        print("3. Search for a roll number")
        print("4. Add new roll number")
        print("5. Replace an existing roll number (e.g., assign a dummy)")
        print("6. Show dummy list")
        print("7. Reset Everyone outside")
        print("8. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_inside(cursor)
        elif choice == "2":
            show_all(cursor)
        elif choice == "3":
            roll = input("Enter roll number to search: ").strip()
            search_roll(cursor, roll)
        elif choice == "4":
            roll = input("Enter new roll number to add: ").strip()
            name = input("Enter name (optional): ").strip() or None
            add_roll(cursor, conn, roll, name)
        elif choice == "5":
            old = input("Enter existing roll number to replace: ").strip()
            print("Choose new roll source:")
            print("  1) Enter new roll manually")
            print("  2) Pick from dummy_rolls.txt")
            src = input("choice (1/2): ").strip()
            new = None
            remove_dummy = False
            new_name = None
            if src == "1":
                new = input("Enter new roll number: ").strip()
                new_name = input("Enter name for the new roll (leave blank to keep old name): ").strip() or None
            elif src == "2":
                dummies = load_dummy_list()
                if not dummies:
                    print(f"No dummy rolls found in {DUMMY_FILE}.")
                    continue
                print("Dummy rolls:")
                for i, d in enumerate(dummies, 1):
                    print(f" {i}. {d}")
                sel = input("Select dummy by number: ").strip()
                try:
                    idx = int(sel) - 1
                    if idx < 0 or idx >= len(dummies):
                        print("Invalid selection.")
                        continue
                    new = dummies[idx]
                    new_name = input("Enter name for the new roll (leave blank to keep old name): ").strip() or None
                    yn = input("Remove this dummy from the dummy list after use? (y/N): ").strip().lower()
                    remove_dummy = (yn == "y")
                except ValueError:
                    print("Invalid selection.")
                    continue
            else:
                print("Invalid choice.")
                continue

            if new:
                replace_roll(cursor, conn, old, new, new_name, remove_dummy)
        elif choice == "6":
            items = load_dummy_list()
            print("\nDummy rolls (from dummy_rolls.txt):")
            if not items:
                print(" (none)")
            else:
                for it in items:
                    print(" -", it)
        elif choice == "7":
            confirm = input("Are you sure you want to set everyone to Outside? (y/N): ").strip().lower()
            if confirm == "y":
                reset_everyone_outside(cursor, conn)
            else:
                print("Cancelled.")
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

    conn.close()

if __name__ == "__main__":
    main()
