from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Event, Schedule, Scheduler, _PRIORITY_ORDER

# Setup
scheduler = Scheduler(id=1)
owner = Owner(name="Alex", id=1, scheduler=scheduler)

buddy = Pet(name="Buddy", id=1, species="Dog", breed="Labrador")
whiskers = Pet(name="Whiskers", id=2, species="Cat", breed="Tabby")
owner.add_pet(buddy)
owner.add_pet(whiskers)

# Tasks for Buddy
walk    = Task(name="Morning Walk",    id=1, type="exercise",  duration=30, recurring=True,  priority="high",   description="Walk around the block",      status="pending", frequency="daily")
feeding = Task(name="Breakfast",       id=2, type="feeding",   duration=10, recurring=True,  priority="high",   description="Feed 2 cups dry food",       status="pending", frequency="daily")
bath    = Task(name="Bath Time",       id=3, type="grooming",  duration=20, recurring=False, priority="medium", description="Weekly bath",                status="pending", frequency="weekly")

# Tasks for Whiskers
brush   = Task(name="Brushing",        id=4, type="grooming",  duration=10, recurring=True,  priority="low",    description="Brush coat",                 status="pending")
play    = Task(name="Playtime",        id=5, type="exercise",  duration=15, recurring=True,  priority="medium", description="Laser pointer session",      status="pending")
meds    = Task(name="Give Medication", id=6, type="medical",   duration=5,  recurring=True,  priority="high",   description="Administer flea prevention", status="pending")

buddy.add_task(walk)
buddy.add_task(feeding)
buddy.add_task(bath)

whiskers.add_task(brush)
whiskers.add_task(play)
whiskers.add_task(meds)

# Schedule events at different times today
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

event_morning = Event(id=1, datetime=(today + timedelta(hours=7)).isoformat())
event_noon    = Event(id=2, datetime=(today + timedelta(hours=12)).isoformat())
event_evening = Event(id=3, datetime=(today + timedelta(hours=18)).isoformat())

scheduler.schedule_task(walk,    event_morning, Schedule(id=1), pets=owner.pets)
scheduler.schedule_task(feeding, event_morning, Schedule(id=1), pets=owner.pets)
scheduler.schedule_task(bath,    event_noon,    Schedule(id=2), pets=owner.pets)
scheduler.schedule_task(brush,   event_morning, Schedule(id=1), pets=owner.pets)
scheduler.schedule_task(play,    event_noon,    Schedule(id=2), pets=owner.pets)
scheduler.schedule_task(meds,    event_evening, Schedule(id=3), pets=owner.pets)

schedule = Schedule(id=10)
schedule.add_event(event_morning)
schedule.add_event(event_noon)
schedule.add_event(event_evening)
scheduler.add_schedule(schedule)

# Demo conflict detection: schedule bath for Buddy at morning (already has walk + feeding there)
scheduler.schedule_task(bath, event_morning, schedule, pets=owner.pets)

# Print today's schedule
print("\nToday's Schedule")
print("=" * 40)
upcoming = scheduler.get_upcoming_tasks(owner, window=1)
print(f"({len(upcoming)} task(s) scheduled in the next 24 hours)")
for event in schedule.get_events(sort=True):
    time_str = event.get_time()
    print(f"\n{time_str}")
    for task in event.get_tasks():
        pet_name = next((p.name for p in owner.pets if p.id == task.pet_id), "Unknown")
        recur_tag = " [R]" if task.recurring else ""
        print(f"  [{pet_name}] {task.get_name()}{recur_tag} ({task.get_duration()} min) — {task.get_priority()} priority")

task_time = {id(t): e.get_time() for s in scheduler.schedules for e in s.events for t in e.tasks}

print("\nAll Tasks by Priority")
print("=" * 40)
for task in scheduler.get_tasks_sorted_by_priority(owner):
    pet_name = next((p.name for p in owner.pets if p.id == task.pet_id), "Unknown")
    recur_tag = " [R]" if task.recurring else ""
    time_str = task_time.get(id(task), "No time")
    print(f"  [{task.get_priority().upper()}] [{pet_name}] {task.get_name()}{recur_tag} ({task.get_duration()} min) @ {time_str}")

# Add extra tasks out of order (evening task first, then morning)
nap     = Task(name="Afternoon Nap",   id=7, type="rest",     duration=60, recurring=False, priority="low",    description="Let Buddy rest",             status="pending")
groom   = Task(name="Nail Trim",       id=8, type="grooming", duration=15, recurring=False, priority="medium", description="Trim Whiskers' nails",       status="complete")
checkup = Task(name="Vet Checkup",     id=9, type="medical",  duration=45, recurring=False, priority="high",   description="Annual checkup",             status="pending")

buddy.add_task(nap)
whiskers.add_task(groom)
buddy.add_task(checkup)

event_late = Event(id=4, datetime=(today + timedelta(hours=20)).isoformat())
scheduler.schedule_task(checkup, event_late,    schedule, pets=owner.pets)
scheduler.schedule_task(nap,     event_noon,    schedule, pets=owner.pets)
scheduler.schedule_task(groom,   event_morning, schedule, pets=owner.pets)

task_time = {id(t): e.get_time() for s in scheduler.schedules for e in s.events for t in e.tasks}

# Demo sort_by_time
print("\nAll Tasks Sorted by Time")
print("=" * 40)
all_tasks = scheduler.get_tasks_by_owner(owner)
for task in scheduler.sort_by_time(all_tasks):
    pet_name = next((p.name for p in owner.pets if p.id == task.pet_id), "Unknown")
    time_str = task_time.get(id(task), "No time")
    print(f"  [{time_str}] [{pet_name}] {task.get_name()} — {task.get_status()}")

# Demo get_tasks_by_pet_name
def sort_tasks_by_time_then_priority(tasks):
    return sorted(
        tasks,
        key=lambda t: (
            tuple(map(int, task_time[id(t)].split(":"))) if id(t) in task_time and task_time[id(t)] else (24, 0),
            _PRIORITY_ORDER.get(t.priority, 99),
        ),
    )

print("\nTasks for Buddy")
print("=" * 40)
for task in sort_tasks_by_time_then_priority(scheduler.get_tasks_by_pet_name(owner, "Buddy")):
    time_str = task_time.get(id(task), "No time")
    print(f"  [{time_str}] {task.get_name()} ({task.get_priority()} priority) — {task.get_status()}")

print("\nTasks for Whiskers")
print("=" * 40)
for task in sort_tasks_by_time_then_priority(scheduler.get_tasks_by_pet_name(owner, "Whiskers")):
    time_str = task_time.get(id(task), "No time")
    print(f"  [{time_str}] {task.get_name()} ({task.get_priority()} priority) — {task.get_status()}")

print("\nMedications")
print("=" * 40)
for pet in owner.get_pets():
    meds = pet.get_medications()
    if meds:
        for med in meds:
            print(f"  [{pet.get_name()}] {med.get_name()} — {med.get_dosage()}, {med.get_frequency()}")
    else:
        print(f"  [{pet.get_name()}] No medications.")

print("\nRecurring Task Auto-Creation Demo")
print("=" * 40)
new_walk = scheduler.mark_task_complete(walk, schedule=schedule, pet=buddy)
if new_walk:
    next_event = next(
        (e for s in scheduler.schedules for e in s.events if new_walk in e.tasks),
        None,
    )
    next_dt = next_event.datetime if next_event else "not scheduled"
    print(f"  Completed: {walk.get_name()} -> status={walk.get_status()}")
    print(f"  Next occurrence: {new_walk.get_name()} scheduled at {next_dt} (status={new_walk.get_status()})")

print("\nHave a great day!\n")
