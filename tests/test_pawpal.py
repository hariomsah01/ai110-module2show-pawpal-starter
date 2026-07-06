"""Tests for the PawPal+ logic layer."""

import os
import sys

# Make the project root importable so `import pawpal_system` works when
# pytest is run from anywhere.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip the task's completed status."""
    task = Task("Morning walk", 30, priority="high")

    assert task.completed is False  # starts incomplete

    task.mark_complete()

    assert task.completed is True  # now marked done


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task count by one."""
    pet = Pet(name="Biscuit", species="dog")

    assert len(pet.list_tasks()) == 0  # no tasks yet

    pet.add_task(Task("Feeding", 10, priority="high"))

    assert len(pet.list_tasks()) == 1  # one task after adding
