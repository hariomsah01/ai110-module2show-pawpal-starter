"""PawPal+ logic layer.

Backend classes for the PawPal+ pet-care planner. This module holds the
"business logic" (data models + scheduling) and is intentionally decoupled
from the Streamlit UI in app.py.

Built CLI-first: everything here can be exercised and verified from a plain
script (see the __main__ demo at the bottom) before wiring up Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Higher number = more important. Used to sort tasks correctly instead of
# comparing the priority strings directly (which would sort alphabetically).
PRIORITY_RANK: dict[str, int] = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, grooming, etc.)."""

    name: str
    duration: int  # minutes
    priority: str = "medium"  # "high" | "medium" | "low"
    category: str = "general"  # walk | feeding | meds | enrichment | grooming
    recurrence: str = "daily"  # daily | weekly | one-time
    preferred_time: str | None = None  # e.g., "08:00" or None
    pet_name: str | None = None  # which pet this task is for (shown in the plan)
    completed: bool = False  # completion status

    def priority_rank(self) -> int:
        """Return the numeric rank for this task's priority (unknown -> 0)."""
        return PRIORITY_RANK.get(self.priority.lower(), 0)

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task outranks `other` by priority."""
        return self.priority_rank() > other.priority_rank()

    def matches_day(self, day: str | None = None) -> bool:
        """Return True if this task should appear in the plan for `day`.

        - "daily": always applies.
        - "one-time": applies only while it is not yet completed.
        - "weekly": applies (a specific weekday could be added later).
        """
        if self.recurrence == "one-time":
            return not self.completed
        return True

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def describe(self) -> str:
        """Return a readable one-line summary of the task."""
        who = f" for {self.pet_name}" if self.pet_name else ""
        return f"{self.name}{who} ({self.duration} min) [priority: {self.priority}]"


@dataclass
class Pet:
    """An individual animal being cared for."""

    name: str
    species: str = "dog"
    breed: str | None = None
    age: int | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a care task to this pet (stamps the task with the pet's name)."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet (no error if it isn't present)."""
        if task in self.tasks:
            self.tasks.remove(task)

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    """The pet owner, their time budget, and preferences."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet."""
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        """Update how much time the owner has today."""
        self.available_minutes = max(0, minutes)

    def update_preferences(self, prefs: dict) -> None:
        """Merge in new owner preferences."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> list[Task]:
        """Gather every task across all pets into one flat list.

        This is how the Scheduler gets its data: it asks the Owner for all
        tasks rather than reaching into each pet directly.
        """
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.list_tasks())
        return all_tasks


class Scheduler:
    """Turns a pool of tasks + a time budget into an ordered daily plan."""

    def __init__(
        self,
        tasks: list[Task] | None = None,
        available_minutes: int = 0,
        strategy: str = "priority",
    ) -> None:
        """Create a Scheduler with a task pool, time budget, and sort strategy."""
        self.tasks: list[Task] = tasks or []
        self.available_minutes = available_minutes
        self.strategy = strategy
        self.skipped: list[Task] = []  # tasks that didn't fit (with reasons in explain())

    @classmethod
    def from_owner(cls, owner: Owner, strategy: str = "priority") -> "Scheduler":
        """Build a Scheduler straight from an Owner's pets and time budget."""
        return cls(
            tasks=owner.get_all_tasks(),
            available_minutes=owner.available_minutes,
            strategy=strategy,
        )

    def sort_tasks(self) -> list[Task]:
        """Order tasks by priority (high first), then shorter duration first."""
        return sorted(
            self.tasks,
            key=lambda t: (-t.priority_rank(), t.duration),
        )

    def filter_tasks(self, day: str | None = None) -> list[Task]:
        """Keep only tasks that apply today and aren't already completed."""
        return [t for t in self.tasks if t.matches_day(day) and not t.completed]

    def resolve_conflicts(self, ordered: list[Task]) -> list[Task]:
        """Greedily fit tasks into the time budget; overflow goes to `skipped`.

        Kept simple: we pack tasks in the given order until the remaining time
        can't hold the next one, then set it aside instead of overlapping it.
        """
        self.skipped = []
        plan: list[Task] = []
        remaining = self.available_minutes
        for task in ordered:
            if task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration
            else:
                self.skipped.append(task)
        return plan

    def generate_plan(self, day: str | None = None) -> list[Task]:
        """Produce the final ordered daily plan that fits the time budget."""
        self.tasks = self.filter_tasks(day)
        ordered = self.sort_tasks()
        return self.resolve_conflicts(ordered)

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        lines = [
            f"Strategy: {self.strategy} (higher priority first, then shorter tasks).",
            f"Time budget: {self.available_minutes} min.",
        ]
        if self.skipped:
            names = ", ".join(t.name for t in self.skipped)
            lines.append(f"Skipped (not enough time): {names}.")
        else:
            lines.append("All eligible tasks fit within the available time.")
        return "\n".join(lines)


if __name__ == "__main__":
    # CLI-first check: build a tiny scenario and print the plan.
    owner = Owner(name="Sam", available_minutes=60)
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    biscuit.add_task(Task("Morning walk", 30, priority="high", category="walk"))
    biscuit.add_task(Task("Feeding", 10, priority="high", category="feeding"))
    biscuit.add_task(Task("Enrichment puzzle", 20, priority="low", category="enrichment"))
    biscuit.add_task(Task("Grooming", 25, priority="medium", category="grooming"))
    owner.add_pet(biscuit)

    scheduler = Scheduler.from_owner(owner)
    plan = scheduler.generate_plan()

    print(f"Daily plan for {owner.name}:")
    for task in plan:
        print(f"  - {task.describe()}")
    print("\n" + scheduler.explain())
