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


def test_sort_by_time_returns_chronological_order():
    owner = Owner(name="Jordan", available_start="07:00", available_end="19:00")
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)

    # Create tasks with different start times (out of order)
    t1 = Task(title="Evening walk", duration_minutes=30, priority="high", start_time="18:00")
    t2 = Task(title="Morning feed", duration_minutes=15, priority="high", start_time="08:00")
    t3 = Task(title="Afternoon play", duration_minutes=20, priority="medium", start_time="14:00")
    t4 = Task(title="No time task", duration_minutes=10, priority="low")  # No start_time

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    pet.add_task(t4)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(pet.tasks)

    # Verify chronological order: 08:00, 14:00, 18:00, then no start_time
    assert sorted_tasks[0].title == "Morning feed"
    assert sorted_tasks[1].title == "Afternoon play"
    assert sorted_tasks[2].title == "Evening walk"
    assert sorted_tasks[3].title == "No time task"
