from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import threading

app = FastAPI()
lock = threading.Lock()

# --- DB Setup ---
conn = sqlite3.connect("people.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS people (
    roll_number TEXT PRIMARY KEY,
    inside INTEGER NOT NULL DEFAULT 0
)
""")
conn.commit()

# --- Request Model ---
class PersonRequest(BaseModel):
    roll_number: str

# --- Helper Functions ---
def get_person(roll_number: str):
    cursor.execute("SELECT inside FROM people WHERE roll_number=?", (roll_number,))
    return cursor.fetchone()

def set_status(roll_number: str, inside: bool):
    cursor.execute("""
    UPDATE people SET inside=? WHERE roll_number=?
    """, (int(inside), roll_number))
    if cursor.rowcount == 0:  # no such roll number
        raise ValueError("Roll number not found")
    conn.commit()

# --- API Endpoints ---
@app.post("/enter")
def enter(req: PersonRequest):
    with lock:
        status = get_person(req.roll_number)
        if not status:
            raise HTTPException(status_code=404, detail="Roll number not registered")
        if status[0] == 1:
            raise HTTPException(status_code=400, detail="Person already inside")
        try:
            set_status(req.roll_number, True)
        except ValueError:
            raise HTTPException(status_code=404, detail="Roll number not registered")
        return {"message": f"{req.roll_number} entered"}

@app.post("/exit")
def exit(req: PersonRequest):
    with lock:
        status = get_person(req.roll_number)
        if not status:
            raise HTTPException(status_code=404, detail="Roll number not registered")
        if status[0] == 0:
            raise HTTPException(status_code=400, detail="Person not inside")
        try:
            set_status(req.roll_number, False)
        except ValueError:
            raise HTTPException(status_code=404, detail="Roll number not registered")
        return {"message": f"{req.roll_number} exited"}
    