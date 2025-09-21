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

def show_count(cursor):
    cursor.execute("SELECT COUNT(*) FROM people WHERE inside=1")
    (count,) = cursor.fetchone()

    print(f"\nPeople inside: {count}")

def remove_rol(conn,cursor,roll_number):
    cursor.execute("SELECT 1 FROM people WHERE roll_number=?", (roll_number,))
    if cursor.fetchone() is None:
        print(f"\nRoll number {roll_number} not found, cannot Delete.")
        return
    cursor.execute("DELETE FROM people WHERE roll_number=?", (roll_number,))
    conn.commit()
    print(f"\Dneleted roll number {roll_number}")

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

def edit_roll(conn, cursor, roll_number, new_name):
    cursor.execute("SELECT 1 FROM people WHERE roll_number=?", (roll_number,))
    if cursor.fetchone() is None:
        print(f"\nRoll number {roll_number} not found, cannot update.")
        return
    cursor.execute("UPDATE people SET name=? WHERE roll_number=?", (new_name, roll_number))
    conn.commit()
    print(f"\nUpdated roll number {roll_number} → new name: {new_name}")


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
        print("1. Show count of people inside")
        print("2. Show list of people inside")
        print("3. Show entire database")
        print("4. Search for a roll number")
        print("5. Edit a roll number")
        print("6. Reset Everyone outside")
        print("7. Delete Roll")
        print("8. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_count(cursor)
        elif choice == "2":
            show_inside(cursor)
        elif choice == "3":
            show_all(cursor)
        elif choice == "4":
            roll = input("Enter roll number to search: ").strip()
            search_roll(cursor, roll)
        elif choice == "5":
            roll = input("Enter roll number to edit: ").strip()
            name = input("Enter new name: ").strip() or None
            edit_roll(conn, cursor, roll, name)
        elif choice == "6":
            confirm = input("Are you sure you want to set everyone to Outside? (y/N): ").strip().lower()
            if confirm == "y":
                reset_everyone_outside(cursor, conn)
            else:
                print("Cancelled.")
        elif choice == "7":
            roll = input("Enter roll number to delete: ").strip()
            remove_rol(conn, cursor,roll)
        elif choice =="8":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice, try again.")

    conn.close()

if __name__ == "__main__":
    main()
