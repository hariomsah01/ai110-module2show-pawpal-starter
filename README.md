# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Owner & pet profiles** — track an owner's daily time budget and multiple pets, each with their own care tasks.
- **Sorting by time** — tasks are ordered chronologically by their `HH:MM` start time so the day reads as a timeline (`Scheduler.sort_by_time()`).
- **Priority-aware planning** — the planner packs the most important tasks first, then shorter ones, into the available time (`Scheduler.generate_plan()`).
- **Time-budget filtering** — tasks that don't fit the available minutes are skipped and reported, not silently dropped (`Scheduler.resolve_conflicts()`).
- **Filtering** — view tasks by pet or by completion status (`Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()`).
- **Conflict warnings** — flags two tasks scheduled at the same start time and returns a friendly warning instead of crashing (`Scheduler.detect_conflicts()`).
- **Daily / weekly recurrence** — completing a recurring task automatically creates its next occurrence with a due date advanced via `timedelta` (`Pet.mark_task_complete()` + `Task.next_occurrence()`).
- **Explainable plans** — every generated plan comes with a plain-language explanation of the strategy and any skipped tasks (`Scheduler.explain()`).
- **Interactive UI + tested logic** — a Streamlit front end backed by a decoupled logic layer with a passing `pytest` suite.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Below is the terminal output from running `python main.py` — an owner with two
pets whose tasks are added out of order, then sorted, checked for conflicts,
filtered, and regenerated on completion. This is evidence that the logic layer
runs correctly.

```
================================================
  Today's Schedule (sorted by time)
================================================
  08:00  Morning walk for Biscuit (30 min) [priority: high]
  08:00  Feeding for Mittens (5 min) [priority: high]
  14:00  Enrichment puzzle for Biscuit (20 min) [priority: low]
  18:00  Evening walk for Biscuit (30 min) [priority: high]
  20:00  Play session for Mittens (15 min) [priority: low]

------------------------------------------------
  Conflict check
------------------------------------------------
  Conflict at 08:00: Morning walk (Biscuit), Feeding (Mittens)

------------------------------------------------
  Recurring: complete Biscuit's morning walk
------------------------------------------------
  Completed: Morning walk (completed=True)
  Auto-created next occurrence due: 2026-07-06
================================================
```

## 🧪 Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 10 tests):

- **Task state** — `mark_complete()` flips a task's status.
- **Data wiring** — adding a task grows the pet's task list.
- **Sorting** — `sort_by_time()` returns tasks in chronological order, with untimed tasks placed last.
- **Recurrence** — completing a *daily* task creates a new task due the next day (via `timedelta`), while a *one-time* task does not regenerate.
- **Conflict detection** — duplicate start times are flagged, and distinct times raise no false alarms.
- **Edge cases** — a pet with no tasks produces a safe, empty plan; tasks that exceed the time budget are skipped rather than scheduled.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
collected 10 items

tests\test_pawpal.py ..........                                          [100%]

============================= 10 passed in 0.08s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**

All core behaviors — sorting, recurrence, conflict detection, filtering, and the time-budget constraint — are covered by passing tests, including several edge cases. It's 4 rather than 5 stars because conflict detection only checks exact time matches (not overlapping durations; see reflection 2b), and weekly recurrence on specific weekdays isn't yet tested.

## 📐 Smarter Scheduling

These algorithmic features make PawPal+ more than a static task list. Each row
names the method in `pawpal_system.py` that implements it.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by time | `Scheduler.sort_by_time()` | Orders tasks by `preferred_time` ("HH:MM"); zero-padded strings sort like real clock times, untimed tasks go last. |
| Sort by priority | `Scheduler.sort_tasks()` | High priority first, then shorter duration (used by `generate_plan()`). |
| Filter by status | `Scheduler.filter_by_status(completed=False)` | Returns completed vs. pending tasks. |
| Filter by pet | `Scheduler.filter_by_pet(pet_name)` | Returns only one pet's tasks. |
| Filter by time budget | `Scheduler.resolve_conflicts()` | Greedily drops tasks that don't fit the available minutes. |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns warning strings for tasks sharing the same start time (exact-match; see reflection 2b). Never crashes. |
| Recurring tasks | `Task.next_occurrence()` + `Pet.mark_task_complete()` | Completing a daily/weekly task auto-creates the next occurrence with a `due_date` advanced via `timedelta`. |

## 📸 Demo Walkthrough

Launch the interactive app with:

```bash
streamlit run app.py
```

### Main UI features

- **👤 Owner** — set the owner's name and the total minutes available for pet care today.
- **🐶 Add a Pet** — create a pet profile (name, species, breed). An owner can have several pets.
- **📝 Add a Task** — pick which pet the task is for, then set its title, duration, priority, category, preferred time (`HH:MM`), and how often it repeats.
- **📋 Current Pets & Tasks** — see each pet's tasks in a table, including time, priority, recurrence, and completion status.
- **📅 Today's Schedule** — click **Generate schedule** to build and view the day's plan.

### Example workflow

1. Set your available time (e.g., `90` minutes) and add an owner name.
2. **Add a pet** — e.g., "Biscuit," a Golden Retriever.
3. **Add tasks** for Biscuit — a `08:00` morning walk (high priority) and a `08:00` feeding, plus a `14:00` enrichment puzzle (low priority).
4. Add a second pet, "Mittens," and give her a `08:00` feeding too.
5. Click **Generate schedule** to view today's plan.

### Key Scheduler behaviors shown

- **Sorting** — the plan is displayed as a clean, time-ordered table (earliest task first).
- **Conflict warnings** — because two tasks are booked at `08:00`, the app shows a yellow warning: *"Conflict at 08:00: Morning walk (Biscuit), Feeding (Mittens)"* — presented at the top of the schedule so it's impossible to miss.
- **Time-budget filtering** — if the day's tasks exceed the available minutes, the extras are listed under a "Skipped" warning rather than silently dropped.
- **Explanation** — an expandable "Why this plan?" panel summarizes the strategy and any skipped tasks.
- **Recurrence** — marking a daily task complete regenerates it for tomorrow (see CLI output below).

### Sample CLI output (`python main.py`)

```
================================================
  Today's Schedule (sorted by time)
================================================
  08:00  Morning walk for Biscuit (30 min) [priority: high]
  08:00  Feeding for Mittens (5 min) [priority: high]
  14:00  Enrichment puzzle for Biscuit (20 min) [priority: low]
  18:00  Evening walk for Biscuit (30 min) [priority: high]
  20:00  Play session for Mittens (15 min) [priority: low]

------------------------------------------------
  Conflict check
------------------------------------------------
  Conflict at 08:00: Morning walk (Biscuit), Feeding (Mittens)

------------------------------------------------
  Filter: only Biscuit's tasks
------------------------------------------------
  - Evening walk for Biscuit (30 min) [priority: high]
  - Morning walk for Biscuit (30 min) [priority: high]
  - Enrichment puzzle for Biscuit (20 min) [priority: low]

------------------------------------------------
  Recurring: complete Biscuit's morning walk
------------------------------------------------
  Completed: Morning walk (completed=True)
  Auto-created next occurrence due: 2026-07-06

------------------------------------------------
  Filter: completed vs. pending
------------------------------------------------
  Completed: ['Morning walk']
  Pending:   ['Evening walk', 'Enrichment puzzle', 'Morning walk', 'Feeding', 'Play session']
================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
