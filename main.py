"""PawPal+ terminal testing ground.

A temporary script to verify the logic layer works end-to-end from the
terminal before wiring it into the Streamlit UI. Run with: python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # 1. Create an owner with a daily time budget.
    owner = Owner(name="Sam", available_minutes=90)

    # 2. Create two pets.
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    mittens = Pet(name="Mittens", species="cat", breed="Tabby")

    # 3. Add tasks OUT OF ORDER (by time) so sorting has something to do.
    #    Note the two 08:00 tasks — used to trigger conflict detection.
    biscuit.add_task(Task("Evening walk", 30, priority="high", preferred_time="18:00"))
    biscuit.add_task(Task("Morning walk", 30, priority="high", preferred_time="08:00"))
    biscuit.add_task(Task("Enrichment puzzle", 20, priority="low", preferred_time="14:00"))
    mittens.add_task(Task("Feeding", 5, priority="high", preferred_time="08:00"))
    mittens.add_task(Task("Play session", 15, priority="low", preferred_time="20:00"))

    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    scheduler = Scheduler.from_owner(owner)

    # --- Sorting by time -----------------------------------------------------
    print("=" * 48)
    print("  Today's Schedule (sorted by time)")
    print("=" * 48)
    for task in scheduler.sort_by_time():
        when = task.preferred_time or "--:--"
        print(f"  {when}  {task.describe()}")

    # --- Conflict detection --------------------------------------------------
    print("\n" + "-" * 48)
    print("  Conflict check")
    print("-" * 48)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")

    # --- Filtering by pet ----------------------------------------------------
    print("\n" + "-" * 48)
    print("  Filter: only Biscuit's tasks")
    print("-" * 48)
    for task in scheduler.filter_by_pet("Biscuit"):
        print(f"  - {task.describe()}")

    # --- Recurring tasks -----------------------------------------------------
    print("\n" + "-" * 48)
    print("  Recurring: complete Biscuit's morning walk")
    print("-" * 48)
    morning_walk = biscuit.list_tasks()[1]  # the 08:00 morning walk
    upcoming = biscuit.mark_task_complete(morning_walk)
    print(f"  Completed: {morning_walk.name} (completed={morning_walk.completed})")
    if upcoming:
        print(f"  Auto-created next occurrence due: {upcoming.due_date}")

    # --- Filtering by status -------------------------------------------------
    scheduler = Scheduler.from_owner(owner)  # refresh to include the new task
    print("\n" + "-" * 48)
    print("  Filter: completed vs. pending")
    print("-" * 48)
    print(f"  Completed: {[t.name for t in scheduler.filter_by_status(True)]}")
    print(f"  Pending:   {[t.name for t in scheduler.filter_by_status(False)]}")
    print("=" * 48)


if __name__ == "__main__":
    main()
