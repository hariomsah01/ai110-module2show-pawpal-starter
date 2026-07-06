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

    # 3. Add tasks with different durations and priorities.
    biscuit.add_task(Task("Morning walk", 30, priority="high", category="walk"))
    biscuit.add_task(Task("Feeding", 10, priority="high", category="feeding"))
    biscuit.add_task(Task("Enrichment puzzle", 20, priority="low", category="enrichment"))

    mittens.add_task(Task("Litter cleanup", 10, priority="medium", category="grooming"))
    mittens.add_task(Task("Feeding", 5, priority="high", category="feeding"))
    mittens.add_task(Task("Play session", 15, priority="low", category="enrichment"))

    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    # 4. Build and print today's schedule.
    scheduler = Scheduler.from_owner(owner)
    plan = scheduler.generate_plan()

    print("=" * 40)
    print(f"  Today's Schedule for {owner.name}")
    print("=" * 40)
    for i, task in enumerate(plan, start=1):
        print(f"  {i}. {task.describe()}")
    print("-" * 40)
    print(scheduler.explain())
    print("=" * 40)


if __name__ == "__main__":
    main()
