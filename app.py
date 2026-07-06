import streamlit as st

# Step 1: bring the logic-layer classes into the UI.
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet-care planning assistant. Add pets, add tasks, and generate a daily plan.")

# Step 2: application "memory".
# Streamlit reruns this whole script on every interaction, so anything created
# at the top would be reborn empty each time. We store the Owner in
# st.session_state (a dict that survives reruns) and only create it once.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=90)

owner: Owner = st.session_state.owner


# ---------------------------------------------------------------------------
# Owner settings
# ---------------------------------------------------------------------------
st.subheader("👤 Owner")
col_a, col_b = st.columns(2)
with col_a:
    owner.name = st.text_input("Owner name", value=owner.name)
with col_b:
    owner.set_available_time(
        st.number_input(
            "Time available today (minutes)",
            min_value=0,
            max_value=1440,
            value=owner.available_minutes,
            step=5,
        )
    )

st.divider()


# ---------------------------------------------------------------------------
# Step 3: Wiring UI -> logic. Add a pet.
# ---------------------------------------------------------------------------
st.subheader("🐶 Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    submitted_pet = st.form_submit_button("Add pet")

    if submitted_pet:
        if new_pet_name.strip():
            # Owner.add_pet handles the data; the rerun re-renders the new pet.
            owner.add_pet(Pet(name=new_pet_name.strip(), species=species, breed=breed or None))
            st.success(f"Added {new_pet_name.strip()}.")
        else:
            st.warning("Please enter a pet name.")

st.divider()


# ---------------------------------------------------------------------------
# Add a task to a chosen pet.
# ---------------------------------------------------------------------------
st.subheader("📝 Add a Task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names = [pet.name for pet in owner.pets]
        chosen_pet_name = st.selectbox("For which pet?", pet_names)

        c1, c2, c3 = st.columns(3)
        with c1:
            task_title = st.text_input("Task title", value="Morning walk")
        with c2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with c3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        c4, c5 = st.columns(2)
        with c4:
            category = st.selectbox(
                "Category", ["walk", "feeding", "meds", "enrichment", "grooming", "general"]
            )
        with c5:
            preferred_time = st.text_input(
                "Preferred time (HH:MM)", value="08:00", help="24-hour, e.g. 08:00 or 18:30"
            )
        recurrence = st.selectbox("Repeats", ["daily", "weekly", "one-time"])
        submitted_task = st.form_submit_button("Add task")

        if submitted_task:
            # Find the chosen Pet object and let it handle the new task.
            pet = next(p for p in owner.pets if p.name == chosen_pet_name)
            pet.add_task(
                Task(
                    name=task_title.strip() or "Untitled task",
                    duration=int(duration),
                    priority=priority,
                    category=category,
                    preferred_time=preferred_time.strip() or None,
                    recurrence=recurrence,
                )
            )
            st.success(f"Added '{task_title}' for {chosen_pet_name}.")

st.divider()


# ---------------------------------------------------------------------------
# Show current pets and their tasks.
# ---------------------------------------------------------------------------
st.subheader("📋 Current Pets & Tasks")
if not owner.pets:
    st.info("No pets yet.")
else:
    for pet in owner.pets:
        label = f"{pet.name} ({pet.species}"
        label += f", {pet.breed})" if pet.breed else ")"
        with st.expander(label, expanded=True):
            tasks = pet.list_tasks()
            if tasks:
                st.table(
                    [
                        {
                            "Time": t.preferred_time or "—",
                            "Task": t.name,
                            "Duration (min)": t.duration,
                            "Priority": t.priority,
                            "Category": t.category,
                            "Repeats": t.recurrence,
                            "Done": "✓" if t.completed else "",
                        }
                        for t in tasks
                    ]
                )
            else:
                st.caption("No tasks yet.")

st.divider()


# ---------------------------------------------------------------------------
# Generate the daily schedule via the Scheduler.
# ---------------------------------------------------------------------------
st.subheader("📅 Today's Schedule")
if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler.from_owner(owner)

    # Conflict warnings first, so the owner sees clashes before the plan.
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        st.warning(f"⚠️ {warning}")

    plan = scheduler.generate_plan()

    if not plan:
        st.info("No tasks could be scheduled. Add tasks or increase available time.")
    else:
        st.success(f"Planned {len(plan)} task(s) within {owner.available_minutes} minutes.")

        # Present the plan as a professional, time-ordered timeline table.
        timeline = Scheduler(tasks=plan).sort_by_time()
        st.table(
            [
                {
                    "Time": t.preferred_time or "—",
                    "Task": t.name,
                    "Pet": t.pet_name or "—",
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                }
                for t in timeline
            ]
        )

    # Show anything that didn't fit in the time budget.
    if scheduler.skipped:
        skipped_names = ", ".join(t.name for t in scheduler.skipped)
        st.warning(f"Skipped (not enough time): {skipped_names}")

    with st.expander("Why this plan?", expanded=True):
        st.text(scheduler.explain())
