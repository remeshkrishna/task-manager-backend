from enum import Enum

class Priority(str,Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class Status(str,Enum):
    in_progress = "In Progress"
    pending = "Pending"
    completed = "Completed"