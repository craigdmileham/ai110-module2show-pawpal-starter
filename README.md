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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
========================================

07:00:00
  [Buddy] Morning Walk (30 min) — high priority
  [Buddy] Breakfast (10 min) — high priority
  [Whiskers] Brushing (10 min) — low priority

12:00:00
  [Buddy] Bath Time (20 min) — medium priority
  [Whiskers] Playtime (15 min) — medium priority

18:00:00
  [Whiskers] Give Medication (5 min) — high priority

Have a great day!

```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.get_tasks_sorted_by_priority` | Returns all tasks for an owner ordered high → medium → low. Tasks with an unrecognized priority are placed last. Uses the module-level `_PRIORITY_ORDER` mapping so the ordering is consistent everywhere. |
| Sort by scheduled time | `Scheduler.sort_by_time` | Sorts a task list by the earliest event time (HH:MM) each task appears in. Tasks not linked to any scheduled event are placed at the end as `(24, 0)` so they don't get lost. |
| Filter by status | `Scheduler.get_tasks_by_status` | Returns only the tasks whose `status` field matches the requested value (e.g., `"pending"`, `"complete"`). |
| Filter by priority | `Scheduler.get_tasks_by_priority` | Returns only tasks whose `priority` field matches the requested level (e.g., `"high"`). |
| Filter by upcoming window | `Scheduler.get_upcoming_tasks` | Returns tasks whose scheduled event falls within the next N days. Parses ISO-format datetimes and deduplicates tasks that appear in multiple events. |
| Conflict detection | `Scheduler.schedule_task` | Before adding a task to an event, inspects existing tasks for same-pet conflicts (two tasks for the same pet at the same time) and cross-pet conflicts (two different pets at the same time slot). Warnings are printed and returned but are non-blocking — the task is always added. |
| Recurring tasks | `Scheduler.mark_task_complete` | When a task has a `frequency` of `"daily"` or `"weekly"` and a schedule is provided, marking it complete automatically creates a new pending copy offset by 1 or 7 days respectively, adds it to the pet, and schedules it in a new Event. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
