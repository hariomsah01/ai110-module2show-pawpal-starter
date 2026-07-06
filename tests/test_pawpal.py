"""Tests for the PawPal+ logic layer.

Covers the core behaviors: task state, sorting, recurrence, conflict
detection, filtering, and the time-budget scheduling constraint. Includes
edge cases (untimed tasks, one-time tasks, a pet with no tasks).
"""

import os
import sys
from datetime import date, timedelta

# Make the project root importable so `import pawpal_system` works when
# pytest is run from anywhere.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Basic task / pet behavior (happy paths)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------
def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return tasks ordered earliest -> latest."""
    tasks = [
        Task("Evening walk", 30, preferred_time="18:00"),
        Task("Morning walk", 30, preferred_time="08:00"),
        Task("Afternoon play", 20, preferred_time="14:00"),
    ]
    scheduler = Scheduler(tasks=tasks)

    ordered = scheduler.sort_by_time()
    times = [t.preferred_time for t in ordered]

    assert times == ["08:00", "14:00", "18:00"]


def test_sort_by_time_puts_untimed_tasks_last():
    """Tasks with no preferred_time should sort to the end."""
    tasks = [
        Task("No time task", 15, preferred_time=None),
        Task("Morning walk", 30, preferred_time="08:00"),
    ]
    scheduler = Scheduler(tasks=tasks)

    ordered = scheduler.sort_by_time()

    assert ordered[0].preferred_time == "08:00"
    assert ordered[-1].preferred_time is None


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------
def test_completing_daily_task_creates_next_day_task():
    """Completing a daily task should create a new task due tomorrow."""
    pet = Pet(name="Biscuit")
    task = Task("Morning walk", 30, recurrence="daily", due_date=date.today())
    pet.add_task(task)

    upcoming = pet.mark_task_complete(task)

    assert task.completed is True  # original is done
    assert upcoming is not None  # a new occurrence was created
    assert upcoming.completed is False  # and it's fresh
    assert upcoming.due_date == date.today() + timedelta(days=1)  # due tomorrow
    assert len(pet.list_tasks()) == 2  # original + next occurrence


def test_one_time_task_does_not_recur():
    """Completing a one-time task should NOT create a new occurrence."""
    pet = Pet(name="Biscuit")
    task = Task("Vet visit", 60, recurrence="one-time")
    pet.add_task(task)

    upcoming = pet.mark_task_complete(task)

    assert upcoming is None  # no next occurrence
    assert len(pet.list_tasks()) == 1  # list did not grow


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------
def test_detect_conflicts_flags_duplicate_times():
    """Two tasks at the same time should produce a conflict warning."""
    tasks = [
        Task("Morning walk", 30, preferred_time="08:00", pet_name="Biscuit"),
        Task("Feeding", 5, preferred_time="08:00", pet_name="Mittens"),
    ]
    scheduler = Scheduler(tasks=tasks)

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_detect_conflicts_none_when_times_differ():
    """No conflict should be reported when all times are distinct."""
    tasks = [
        Task("Morning walk", 30, preferred_time="08:00"),
        Task("Evening walk", 30, preferred_time="18:00"),
    ]
    scheduler = Scheduler(tasks=tasks)

    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Edge cases and scheduling constraints
# ---------------------------------------------------------------------------
def test_pet_with_no_tasks_does_not_crash():
    """An owner/pet with no tasks should produce an empty, safe plan."""
    owner = Owner(name="Sam", available_minutes=60)
    owner.add_pet(Pet(name="Ghost"))

    scheduler = Scheduler.from_owner(owner)

    assert scheduler.generate_plan() == []
    assert scheduler.detect_conflicts() == []


def test_scheduler_skips_tasks_that_exceed_time_budget():
    """Tasks that don't fit the available time should be skipped, not planned."""
    owner = Owner(name="Sam", available_minutes=30)
    pet = Pet(name="Biscuit")
    pet.add_task(Task("Short walk", 20, priority="high"))
    pet.add_task(Task("Long hike", 90, priority="high"))  # won't fit in 30 min
    owner.add_pet(pet)

    scheduler = Scheduler.from_owner(owner)
    plan = scheduler.generate_plan()

    planned_names = [t.name for t in plan]
    assert "Short walk" in planned_names
    assert "Long hike" not in planned_names
    assert any(t.name == "Long hike" for t in scheduler.skipped)
