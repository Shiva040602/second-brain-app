from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
import openai

# --------------------
# App init
# --------------------
app = FastAPI()

# --------------------
# OpenAI (optional)
# --------------------
# If you have a key, paste it here.
# If not, leave it empty – app will still work.
openai.api_key = ""   # example: "sk-xxxxxxxx"

# --------------------
# MongoDB
# --------------------
client = MongoClient("mongodb://localhost:27017/")
db = client.second_brain
notes_collection = db.notes

# --------------------
# Data Model
# --------------------
class NoteCreate(BaseModel):
    title: str
    content: str

# --------------------
# Home
# --------------------
@app.get("/")
def home():
    return {"message": "Second Brain Backend is running"}

# --------------------
# AI Summary (safe)
# --------------------
def generate_summary(text: str):
    try:
        if openai.api_key == "":
            return "Summary unavailable (no API key)"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Summarize this note in 2 lines:\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception:
        return "Summary unavailable"

# --------------------
# Create Note
# --------------------
@app.post("/notes")
def add_note(note: NoteCreate):
    summary = generate_summary(note.content)

    note_data = {
        "title": note.title,
        "content": note.content,
        "summary": summary,
        "created_at": datetime.utcnow()
    }

    notes_collection.insert_one(note_data)
    return {"status": "Note added successfully"}

# --------------------
# Get Notes
# --------------------
@app.get("/notes")
def get_notes():
    notes = list(notes_collection.find({}, {"_id": 0}))
    return notes
