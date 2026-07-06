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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One tradeoff my scheduler makes is in conflict detection. The `Scheduler.detect_conflicts()` method only flags tasks that share the **exact same start time** (for example, two tasks both at "08:00"). It does **not** look at how long each task lasts, so it won't catch an *overlap* — like a 30-minute walk at 08:00 running into a feeding at 08:15.

This is reasonable for a pet-care planner because most owners think in simple time slots, and exact-match checking is fast, easy to read, and rarely wrong for short daily tasks. Checking true overlaps would mean parsing every time into minutes and comparing ranges, which adds complexity for a small real-world gain. If the app grew to handle longer, tightly packed schedules, upgrading to real overlap detection would be the natural next step.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
