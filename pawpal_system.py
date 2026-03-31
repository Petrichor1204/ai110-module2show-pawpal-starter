from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict


def _parse_time(value: str) -> int:
    """Convert HH:MM string to minutes since midnight."""
    try:
        parsed = datetime.strptime(value, "%H:%M")
        return parsed.hour * 60 + parsed.minute
    except ValueError as exc:
        raise ValueError(f"Invalid time format: {value}. Expected HH:MM") from exc


def _format_time(minutes: int) -> str:
    """Convert minutes since midnight back to HH:MM."""
    minutes = max(0, min(minutes, 24 * 60 - 1))
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    frequency: Optional[str] = None  # e.g. "daily", "weekly"
    preferred_time: Optional[str] = None  # "morning", "afternoon", "evening"
    is_completed: bool = False

    def __post_init__(self):
        if self.duration_minutes <= 0:
            raise ValueError("Task duration_minutes must be > 0")
        if self.priority.lower() not in ["low", "medium", "high"]:
            raise ValueError("Task priority must be 'low', 'medium', or 'high'")
        self.priority = self.priority.lower()

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed yet."""
        self.is_completed = False

    def get_info(self) -> str:
        """Return a human-readable string describing the task."""
        status = "Done" if self.is_completed else "Pending"
        freq = f", {self.frequency}" if self.frequency else ""
        pref = f", preferred: {self.preferred_time}" if self.preferred_time else ""
        return (
            f"Task('{self.title}', {self.duration_minutes}m, priority={self.priority}{freq}{pref}) "
            f"[{status}]"
        )

    def __repr__(self) -> str:
        return self.get_info()


@dataclass
class Pet:
    name: str
    species: str
    age: int
    breed: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        if not isinstance(task, Task):
            raise TypeError("pet.add_task requires a Task instance")
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title and return whether it existed."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                del self.tasks[i]
                return True
        return False

    def get_info(self) -> str:
        """Return a summary string for this pet."""
        breed = f" ({self.breed})" if self.breed else ""
        return f"{self.name}{breed}: {self.species}, {self.age} years old, {len(self.tasks)} tasks"

    def get_pending_tasks(self) -> List[Task]:
        """Return a list of tasks that are not yet completed."""
        return [task for task in self.tasks if not task.is_completed]


class Owner:
    def __init__(self, name: str, available_start: str, available_end: str):
        self.name = name
        self.available_start = available_start
        self.available_end = available_end
        self.pets: List[Pet] = []

        self._start_minutes = _parse_time(self.available_start)
        self._end_minutes = _parse_time(self.available_end)

        if self._start_minutes >= self._end_minutes:
            raise ValueError("available_start must be before available_end")

    def add_pet(self, pet: Pet) -> None:
        """Add a new pet to the owner's pet collection."""
        if not isinstance(pet, Pet):
            raise TypeError("Owner.add_pet requires a Pet instance")
        if any(existing.name == pet.name for existing in self.pets):
            raise ValueError(f"Owner already has a pet named '{pet.name}'")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Look up a pet by name from the owner."""
        return next((pet for pet in self.pets if pet.name == name), None)

    def get_all_tasks(self, include_completed: bool = False) -> List[Task]:
        """Return all tasks for all pets, optionally including completed tasks."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks if include_completed else [task for task in tasks if not task.is_completed]

    def get_schedule_window(self) -> Tuple[str, str]:
        """Return the owner's available time window as (start, end)."""
        return self.available_start, self.available_end


class Scheduler:
    PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner):
        if not isinstance(owner, Owner):
            raise TypeError("Scheduler requires an Owner instance")
        self.owner = owner
        self.schedule: List[Dict] = []

    def add_task(self, task: Task, pet_name: str) -> None:
        """Add a task for a specific pet in the owner account."""
        if not isinstance(task, Task):
            raise TypeError("Scheduler.add_task requires a Task instance")
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"Pet named '{pet_name}' not found")
        pet.add_task(task)

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority then duration then title."""
        return sorted(
            tasks,
            key=lambda t: (
                self.PRIORITY_RANK.get(t.priority, 3),
                t.duration_minutes,
                t.title,
            ),
        )

    def generate_schedule(self, include_completed: bool = False) -> List[Dict]:
        """Generate a daily schedule for all pending tasks in owner time window."""
        tasks = self.owner.get_all_tasks(include_completed=include_completed)
        if not tasks:
            self.schedule = []
            return []

        tasks = [t for t in tasks if t.duration_minutes > 0]
        tasks = self._sort_tasks(tasks)

        current_minute = _parse_time(self.owner.available_start)
        end_minute = _parse_time(self.owner.available_end)

        plan = []

        for task in tasks:
            if task.is_completed:
                continue
            task_end = current_minute + task.duration_minutes
            if task_end > end_minute:
                continue
            pet_of_task = next(
                (pet for pet in self.owner.pets if task in pet.tasks),
                None,
            )
            plan_item = {
                "pet": pet_of_task.name if pet_of_task else "unknown",
                "task": task,
                "start": _format_time(current_minute),
                "end": _format_time(task_end),
                "priority": task.priority,
            }
            plan.append(plan_item)
            current_minute = task_end
        self.schedule = plan
        return plan

    def explain_plan(self) -> str:
        """Provide a human-readable explanation of the generated schedule."""
        if not self.schedule:
            return "No schedule generated yet or no tasks available."

        lines = [f"Schedule for {self.owner.name} ({self.owner.available_start}-{self.owner.available_end}):"]
        for entry in self.schedule:
            lines.append(
                f"{entry['start']} - {entry['end']}: {entry['task'].title} "
                f"for {entry['pet']} [priority={entry['priority']}]"
            )
        return "\n".join(lines)
