from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    status TEXT
)
""")
conn.commit()


class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    status: str


@app.post("/tasks")
def create_task(task: TaskCreate):
    cursor.execute("INSERT INTO tasks(title, status) VALUES (?,?)", (task.title, "todo"))
    conn.commit()
    return {"message": "Task created"}


@app.get("/tasks")
def get_tasks():
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    return [{"id": r[0], "title": r[1], "status": r[2]} for r in rows]


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (task.status, task_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(404, "Task not found")
    return {"message": "Updated"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(404, "Task not found")
    return {"message": "Deleted"}