import sys
from pathlib import Path

# Ensure project root is on sys.path so top-level modules can be imported from tests.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pawpal_system import Pet, Task


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