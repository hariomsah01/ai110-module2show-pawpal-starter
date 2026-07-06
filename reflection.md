# PawPal+ Project Reflection

Add a pet and its details — The user can create a profile for their pet (name, type/breed) so the app knows who it's planning care for.

Add a care task with a duration and priority — The user can enter a task like "morning walk," say how long it takes and how important it is, so it can be scheduled appropriately.

Generate and view today's plan — The user can ask the app to build a daily schedule from their tasks and available time, then see the ordered plan (and why it was arranged that way).

## 1. System Design

**a. Initial design**

My first design used four main classes:

- **Owner** — holds the person's name, how much time they have today, their preferences, and the list of pets they own. It can add a pet, set the available time, and update preferences.
- **Pet** — holds the pet's name, species, breed, and age, plus the list of care tasks for that pet. It can add a task, remove a task, and list its tasks.
- **Task** — one piece of pet care (like a walk or feeding). It holds the name, how long it takes, its priority, its category, how often it repeats, and an optional preferred time. It can compare its priority to another task and describe itself.
- **Scheduler** — the "brain." It takes the tasks and the available time and builds the daily plan. It can sort tasks, filter out ones that don't fit, handle time conflicts, generate the final plan, and explain its choices.

The idea is that an Owner has many Pets, each Pet has many Tasks, and the Scheduler uses those Tasks (plus the time limit) to make the plan. I kept the data classes (Task, Pet) simple and put all the real logic in the Scheduler.

**b. Design changes**

Yes, my design changed a little after the AI reviewed my skeleton.

- **What I changed:** I added a `pet_name` field to the `Task` class.
- **Why:** The AI pointed out a missing relationship. Once the Scheduler mixes all the pets' tasks into one list, there was no way to tell which pet each task belonged to. So the final plan couldn't say "Morning walk — for Biscuit." Adding `pet_name` keeps that link so the plan can show the right pet next to each task.
- **One thing I noticed but did NOT change yet:** The AI also warned that `priority` is a text value ("high"/"medium"/"low"). If I sort those words directly, Python sorts them alphabetically, which is wrong. I left the skeleton as-is for now, but I'll fix this in the Scheduler by mapping each priority to a number before sorting.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three main constraints:

- **Time available** — the owner sets how many minutes they have, and the scheduler only plans tasks that fit within that budget.
- **Priority** — each task is high, medium, or low, and higher-priority tasks are placed first.
- **Preferred time** — tasks have an `HH:MM` time so the plan can be shown as a real daily timeline, and same-time tasks are flagged as conflicts.

I decided **time** and **priority** mattered most because the whole point of the app is helping a busy owner fit the *important* care into a limited day. If something has to be dropped, it should be the low-priority task, not the medication. Preferred time matters for ordering and conflicts, but it comes after making sure the essential tasks actually fit.

**b. Tradeoffs**

One tradeoff my scheduler makes is in conflict detection. The `Scheduler.detect_conflicts()` method only flags tasks that share the **exact same start time** (for example, two tasks both at "08:00"). It does **not** look at how long each task lasts, so it won't catch an *overlap* — like a 30-minute walk at 08:00 running into a feeding at 08:15.

This is reasonable for a pet-care planner because most owners think in simple time slots, and exact-match checking is fast, easy to read, and rarely wrong for short daily tasks. Checking true overlaps would mean parsing every time into minutes and comparing ranges, which adds complexity for a small real-world gain. If the app grew to handle longer, tightly packed schedules, upgrading to real overlap detection would be the natural next step.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase:

- **Design brainstorming** — to list the main objects and turn my ideas into a Mermaid UML diagram.
- **Skeleton and implementation** — the assistant's automatic editing / agent mode was the most effective feature. It could create files, fill in class stubs, and then flesh out the real logic across `pawpal_system.py`, `main.py`, and `app.py` at once, which saved a lot of typing.
- **Explaining and reviewing** — the chat was helpful for questions like "how do I sort `HH:MM` strings with a lambda?" and "how do I use `timedelta` for the next day?"

The most helpful prompts were **specific ones** that named a file or a method and asked for one concrete thing — for example, "review my skeleton for missing relationships" or "how should the Scheduler get tasks from the Owner?" Vague prompts gave vague answers.

**b. Judgment and verification**

One moment I did not accept a suggestion as-is was the **conflict detection** method. The AI offered a very short, "Pythonic" version using `itertools.groupby`, but it needed the list pre-sorted and was harder to read at a glance. I kept the clearer version that groups tasks into a dictionary by time, because readability mattered more than saving two lines.

I also caught a real bug through verification: the conflict warning first used a ⚠️ emoji, which **crashed in the Windows terminal** (encoding error). I only found this because I actually *ran* `main.py` instead of trusting the code looked fine. I verify AI output by running it — the CLI demo and the `pytest` suite are how I confirm the logic really behaves the way the AI (and I) expected.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 10 automated tests in `tests/test_pawpal.py` covering:

- **Task state** — `mark_complete()` flips a task to done.
- **Data wiring** — adding a task grows the pet's task list.
- **Sorting** — tasks come back in chronological order, and untimed tasks go last.
- **Recurrence** — completing a daily task creates a next-day task, and a one-time task does *not* regenerate.
- **Conflict detection** — duplicate times are flagged, and different times raise no false alarms.
- **Edge cases** — a pet with no tasks doesn't crash, and tasks that exceed the time budget are skipped.

These were important because they are the exact behaviors a user depends on. If sorting, recurrence, or conflict detection quietly broke, the daily plan would be wrong and the owner might miss a walk or a dose of medication.

**b. Confidence**

I'm fairly confident — about **4 out of 5**. All 10 tests pass, and they cover the core logic plus several edge cases. I'm not at 5 because conflict detection only checks exact time matches (not overlapping durations), and I haven't tested weekly recurrence landing on a specific weekday. If I had more time, I would test: overlapping-duration conflicts, weekly tasks across a month boundary, invalid time strings, and a plan where every task is the same priority.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how cleanly the logic layer is separated from the UI. Because `pawpal_system.py` has no Streamlit code in it, I could build and test the whole "brain" from the terminal first, then wire it into `app.py` with confidence. The recurring-task feature (completing a task auto-creating tomorrow's) is the part I think is coolest.

**b. What you would improve**

If I had another iteration, I would upgrade conflict detection to handle **overlapping durations**, not just exact time matches — that's the biggest gap. I'd also let the user **mark tasks complete directly in the Streamlit UI** (right now recurrence is only shown from the CLI), and I'd store real dates so the plan could span multiple days instead of just "today."

**c. Key takeaway**

The biggest thing I learned is what it means to be the **lead architect** while working with a powerful AI assistant. The AI could generate a lot of code very fast, but it was my job to make the design decisions, catch what didn't fit, and verify everything actually worked. Using **separate chat sessions for each phase** helped me stay organized — planning, implementing, and testing didn't bleed into each other, so each conversation stayed focused. The AI was fastest at *writing*, but I was responsible for *deciding* — choosing the readable version over the clever one, spotting the missing pet-to-task link, and running the code instead of assuming it was correct. AI is a strong collaborator, but the direction and the judgment have to come from me.
