from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict
from collections import defaultdict


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
    start_time: Optional[str] = None  # "HH:MM" optional scheduled start time
    due_date: Optional[str] = None  # ISO date "YYYY-MM-DD", optional recurrence anchor
    is_completed: bool = False

    def __post_init__(self):
        if self.start_time is not None:
            _parse_time(self.start_time)  # validate format

        if self.due_date is not None:
            try:
                datetime.fromisoformat(self.due_date)
            except ValueError as exc:
                raise ValueError(f"Invalid due_date format: {self.due_date}. Expected YYYY-MM-DD") from exc

        if self.duration_minutes <= 0:
            raise ValueError("Task duration_minutes must be > 0")
        if self.priority.lower() not in ["low", "medium", "high"]:
            raise ValueError("Task priority must be 'low', 'medium', or 'high'")
        self.priority = self.priority.lower()

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and auto-schedule next recurrence if applicable."""
        self.is_completed = True

        if self.frequency in ("daily", "weekly"):
            # create next occurrence
            days = 1 if self.frequency == "daily" else 7
            next_date = datetime.today().date() + timedelta(days=days)
            next_task = Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                preferred_time=self.preferred_time,
                start_time=self.start_time,
                due_date=next_date.isoformat(),
                is_completed=False,
            )
            return next_task

        return None

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

    def complete_task(self, title: str) -> Optional[Task]:
        """Mark a task as complete by title and auto-add recurrence if generated."""
        for task in self.tasks:
            if task.title == title:
                next_task = task.mark_complete()
                if next_task is not None:
                    self.add_task(next_task)
                return next_task
        raise ValueError(f"Task '{title}' not found")


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

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by HH:MM start_time. Tasks without start_time go to end.

        Args:
            tasks: List of Task objects to sort.

        Returns:
            Sorted list of tasks, with tasks having start_time first (earliest first),
            followed by tasks without start_time.
        """
        return sorted(
            tasks,
            key=lambda t: _parse_time(t.start_time) if t.start_time is not None else float("inf"),
        )

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion state and/or pet name.

        Args:
            completed: If True, return only completed tasks; if False, only pending;
                       if None, ignore completion status.
            pet_name: Name of the pet to filter tasks for; if None, include all pets.

        Returns:
            List of tasks matching the filter criteria.
        """
        filtered: List[Task] = []
        pets = self.owner.pets

        if pet_name is not None:
            pet = self.owner.get_pet(pet_name)
            if pet is None:
                return []
            pets = [pet]

        for pet in pets:
            for task in pet.tasks:
                if completed is not None and task.is_completed != completed:
                    continue
                filtered.append(task)

        return filtered

    def detect_conflicts(self) -> List[str]:
        """Return lightweight conflict warnings for tasks that share the same start_time.

        Scans all tasks (including completed) and groups them by start_time.
        For any time slot with multiple tasks, generates a warning message.

        Returns:
            List of warning strings describing conflicts, or empty list if none.
        """
        tasks = self.owner.get_all_tasks(include_completed=True)
        time_map = defaultdict(list)
        for task in tasks:
            if task.start_time:
                time_map[task.start_time].append(task)

        warnings = []
        for time_slot, tasks_at_time in time_map.items():
            if len(tasks_at_time) > 1:
                titles = [t.title for t in tasks_at_time]
                warnings.append(
                    f"Conflict at {time_slot}: {len(tasks_at_time)} tasks scheduled concurrently ({', '.join(titles)})."
                )
        return warnings

    def generate_schedule(self, include_completed: bool = False) -> Tuple[List[Dict], List[str]]:
        """Generate a daily schedule for all pending tasks in owner time window, and return conflicts."""
        tasks = self.owner.get_all_tasks(include_completed=include_completed)
        if not tasks:
            self.schedule = []
            return [], []

        tasks = [t for t in tasks if t.duration_minutes > 0]
        tasks = self._sort_tasks(tasks)

        current_minute = _parse_time(self.owner.available_start)
        end_minute = _parse_time(self.owner.available_end)

        plan = []
        conflicts = []

        for task in tasks:
            if task.is_completed:
                continue
            task_end = current_minute + task.duration_minutes
            if task_end > end_minute:
                pet_of_task = next(
                    (pet for pet in self.owner.pets if task in pet.tasks),
                    None,
                )
                pet_name = pet_of_task.name if pet_of_task else "unknown"
                conflicts.append(
                    f"Task '{task.title}' for {pet_name} ({task.duration_minutes}m) cannot fit in remaining time."
                )
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
        return plan, conflicts

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
