import sys
from pathlib import Path

# Ensure project root is on sys.path so top-level modules can be imported from tests.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pawpal_system import Owner, Pet, Task, Scheduler


def test_task_completion_marks_done():
    task = Task(title="Grooming", duration_minutes=20, priority="medium")
    assert task.is_completed is False

    task.mark_complete()
    assert task.is_completed is True

    task.mark_incomplete()
    assert task.is_completed is False


def test_pet_add_task_increases_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0

    task = Task(title="Feeding", duration_minutes=10, priority="high")
    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Feeding"


def test_daily_task_completion_creates_next_occurrence():
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(
        title="Feed", duration_minutes=10, priority="high", frequency="daily", start_time="08:00"
    )
    pet.add_task(task)

    next_task = pet.complete_task("Feed")

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.frequency == "daily"
    assert next_task.is_completed is False
    assert next_task.title == "Feed"
    assert next_task.start_time == "08:00"
    assert len(pet.tasks) == 2


def test_scheduler_detects_conflicts_for_same_time():
    owner = Owner(name="Jordan", available_start="07:00", available_end="19:00")
    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Nori", species="cat", age=5)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    t1 = Task(title="Morning walk", duration_minutes=30, priority="high", start_time="08:00")
    t2 = Task(title="Feed", duration_minutes=15, priority="high", start_time="08:00")

    pet1.add_task(t1)
    pet2.add_task(t2)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Morning walk" in warnings[0] and "Feed" in warnings[0]
