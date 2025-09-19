import json
import pydantic
import enum

from datetime import datetime

class TaskStatus(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Task(pydantic.BaseModel):
    id: int
    title: str
    description: str
    status: str = TaskStatus.PENDING.value
    timestamp: str = datetime.now().strftime("%Y-%m-%d")

def get_tasks(path:str="./data/data.json"):
    try:
        with open(path, "r") as f:
            data = json.load(f) 

            return data ["tasks"]
        
    except Exception as e:
        print(f"Error opening tasks file: {e}")

def save_tasks(tasks:list, path:str="./data/data.json"):
    try:
        with open(path, "w") as f:
            json.dump({"tasks": tasks}, f, indent=4)
    except Exception as e:
        print(f"Error saving tasks in {path}: {e}")
         