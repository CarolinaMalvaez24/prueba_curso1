
import json
import pydantic
import enum


from datetime import datetime

class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "In Progress"
    COMPLETED = "COMPLETED"

class Task(pydantic.BaseModel):
    id: int
    title: str
    description: str
    status: str = TaskStatus.PENDING.value
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_tasks(path: str = "./data/data.json"):
    try:
        with open(path, "r") as file:
            data = json.load(file)
            return data["tasks"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading tasks: {e}")
        return []

def save_task(tasks: list, path: str = "./data/data.json"):
    try:
        with open(path, "w") as f:
            json.dump({"tasks": tasks}, f, indent=4)
    except Exception as e:
        print(f"Error saving tasks in {path}: {e}")