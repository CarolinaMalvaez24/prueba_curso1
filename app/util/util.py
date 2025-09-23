import json
import enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator
from pathlib import Path

# ---------- Rutas robustas (independientes del cwd) ----------
BASE_DIR = Path(__file__).resolve().parents[1]  # .../app/
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "data.json"

class TaskStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    timestamp: str = ""

    @field_validator("timestamp")
    @classmethod
    def default_ts(cls, v):
        return v or datetime.now().isoformat()

def _ensure_dir_and_file() -> None:
    """Crea carpeta y JSON con esquema válido si no existen."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"tasks": []}, ensure_ascii=False, indent=4), encoding="utf-8")
        return
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "tasks" not in data or not isinstance(data["tasks"], list):
            raise ValueError("Invalid schema")
    except Exception:
        DATA_FILE.write_text(json.dumps({"tasks": []}, ensure_ascii=False, indent=4), encoding="utf-8")

def _read_all() -> List[dict]:
    _ensure_dir_and_file()
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))["tasks"]

def save_tasks(tasks: List[dict]) -> None:
    _ensure_dir_and_file()
    DATA_FILE.write_text(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=4), encoding="utf-8")

def get_tasks() -> List[dict]:
    return _read_all()

def next_id(tasks: List[dict]) -> int:
    return (max((int(t.get("id", 0)) for t in tasks), default=0) + 1) if tasks else 1

def create_task(title: str, description: str = "", status: TaskStatus = TaskStatus.PENDING) -> Task:
    tasks = _read_all()
    task = Task(id=next_id(tasks), title=title, description=description, status=status)
    tasks.append(task.model_dump())
    save_tasks(tasks)
    return task

def read_task(task_id: int) -> Optional[dict]:
    for t in _read_all():
        if int(t.get("id")) == int(task_id):
            return t
    return None

def update_task(task_id: int, *, title: Optional[str] = None,
                description: Optional[str] = None,
                status: Optional[TaskStatus] = None) -> Optional[dict]:
    tasks = _read_all()
    updated = None
    for t in tasks:
        if int(t.get("id")) == int(task_id):
            if title is not None: t["title"] = title
            if description is not None: t["description"] = description
            if status is not None:
                t["status"] = status.value if isinstance(status, TaskStatus) else str(status)
            updated = t
            break
    if updated is not None:
        save_tasks(tasks)
    return updated

def delete_task(task_id: int) -> bool:
    """Elimina la tarea por id. True si se borró, False si no existía."""
    tasks = _read_all()
    new_tasks = [t for t in tasks if int(t.get("id")) != int(task_id)]
    if len(new_tasks) != len(tasks):
        save_tasks(new_tasks)
        return True
    return False
