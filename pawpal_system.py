"""PawPal+ logic layer.

Backend classes for the PawPal+ pet-care planner. This module holds the
"business logic" (data models + scheduling) and is intentionally decoupled
from the Streamlit UI in app.py.

Class skeletons generated from diagrams/uml_draft.mmd — method bodies are
stubbed and will be implemented incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, grooming, etc.)."""

    name: str
    duration: int  # minutes
    priority: str = "medium"  # "high" | "medium" | "low"
    category: str = "general"  # walk | feeding | meds | enrichment | grooming
    recurrence: str = "daily"  # daily | weekly | one-time
    preferred_time: str | None = None  # e.g., "08:00" or None

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task outranks `other` by priority."""
        raise NotImplementedError

    def matches_day(self, day: str) -> bool:
        """Return True if this (recurring) task applies on the given day."""
        raise NotImplementedError

    def describe(self) -> str:
        """Return a readable one-line summary of the task."""
        raise NotImplementedError


@dataclass
class Pet:
    """An individual animal being cared for."""

    name: str
    species: str = "dog"
    breed: str | None = None
    age: int | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner, their time budget, and preferences."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet."""
        raise NotImplementedError

    def set_available_time(self, minutes: int) -> None:
        """Update how much time the owner has today."""
        raise NotImplementedError

    def update_preferences(self, prefs: dict) -> None:
        """Merge in new owner preferences."""
        raise NotImplementedError


class Scheduler:
    """Turns a pool of tasks + a time budget into an ordered daily plan."""

    def __init__(
        self,
        tasks: list[Task] | None = None,
        available_minutes: int = 0,
        strategy: str = "priority",
    ) -> None:
        self.tasks: list[Task] = tasks or []
        self.available_minutes = available_minutes
        self.strategy = strategy

    def sort_tasks(self) -> list[Task]:
        """Order tasks by the chosen strategy (e.g., priority, then duration)."""
        raise NotImplementedError

    def filter_tasks(self) -> list[Task]:
        """Drop tasks that don't fit within the available time budget."""
        raise NotImplementedError

    def resolve_conflicts(self) -> None:
        """Handle overlapping time slots / preferred-time collisions."""
        raise NotImplementedError

    def generate_plan(self) -> list[Task]:
        """Produce the final ordered daily plan."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        raise NotImplementedError
