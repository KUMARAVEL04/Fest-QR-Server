# Fest-QR-Server

This project provides a simple system to track whether people (identified by **roll numbers**) are **inside** or **outside**.  
It consists of:

- **FastAPI backend (`main.py`)** → Provides REST API endpoints for entering and exiting.  
- **CLI tool (`count.py`)** → Lets you check counts, view all records, and search for a roll number.  
- **Seeder (`seed.py`)** → Bulk insert roll numbers into the database.  
- **SQLite database (`people.db`)** → Stores roll numbers and inside/outside status.  

---
## ⚡ Setup Instructions

### 1. Install dependencies
Make sure you have Python 3.8+ installed. Then:

```bash
pip install fastapi uvicorn
```

SQLite is included with Python by default (no extra install needed).

---

### 2. Seed the database
Before starting, add some roll numbers to the database:

```bash
python seed.py
```

Example input:
```
106123069
106123071
106123073
done
```

This creates/updates `people.db` with those roll numbers.

---

### 3. Run the FastAPI server
Start the backend API (binds to **0.0.0.0** so it’s available on all interfaces):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Now the API is available at:

- `POST /enter` → Mark a roll number as inside  
- `POST /exit` → Mark a roll number as outside  


---

### 4. Use the CLI Tool
To inspect the database manually, run:

```bash
python count.py
```

You’ll get a menu:

```
--- MENU ---
1. Show count and list of people inside
2. Show entire database
3. Search for a roll number
4. Exit
```

Example output:
```
People inside: 2
Roll numbers:
 - 106123069
 - 106123073
```
---