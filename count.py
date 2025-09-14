import sqlite3

def show_inside(cursor):
    cursor.execute("SELECT COUNT(*) FROM people WHERE inside=1")
    (count,) = cursor.fetchone()

    cursor.execute("SELECT roll_number FROM people WHERE inside=1")
    rows = cursor.fetchall()

    print(f"\nPeople inside: {count}")
    if count > 0:
        print("Roll numbers:")
        for row in rows:
            print(" -", row[0])


def show_all(cursor):
    cursor.execute("SELECT roll_number, inside FROM people ORDER BY roll_number")
    rows = cursor.fetchall()

    print("\nDatabase (roll_number | status):")
    for roll, inside in rows:
        status = "Inside" if inside == 1 else "Outside"
        print(f"{roll} | {status}")


def search_roll(cursor, roll_number):
    cursor.execute("SELECT inside FROM people WHERE roll_number=?", (roll_number,))
    row = cursor.fetchone()
    if row is None:
        print(f"\nRoll number {roll_number} not found in database.")
    else:
        status = "Inside" if row[0] == 1 else "Outside"
        print(f"\n{roll_number} is currently: {status}")


def main():
    conn = sqlite3.connect("people.db")
    cursor = conn.cursor()

    while True:
        print("\n--- MENU ---")
        print("1. Show count and list of people inside")
        print("2. Show entire database")
        print("3. Search for a roll number")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_inside(cursor)
        elif choice == "2":
            show_all(cursor)
        elif choice == "3":
            roll = input("Enter roll number to search: ").strip()
            search_roll(cursor, roll)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

    conn.close()


if __name__ == "__main__":
    main()
