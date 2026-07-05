from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Event, Schedule, Scheduler

# Setup
scheduler = Scheduler(id=1)
owner = Owner(name="Alex", id=1, scheduler=scheduler)

buddy = Pet(name="Buddy", id=1, type="Dog", breed="Labrador")
whiskers = Pet(name="Whiskers", id=2, type="Cat", breed="Tabby")
owner.add_pet(buddy)
owner.add_pet(whiskers)

# Tasks for Buddy
walk    = Task(name="Morning Walk",    id=1, type="exercise",  duration=30, recurring=True,  priority="high",   description="Walk around the block",      status="pending")
feeding = Task(name="Breakfast",       id=2, type="feeding",   duration=10, recurring=True,  priority="high",   description="Feed 2 cups dry food",       status="pending")
bath    = Task(name="Bath Time",       id=3, type="grooming",  duration=20, recurring=False, priority="medium", description="Weekly bath",                status="pending")

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

scheduler.schedule_task(walk,    event_morning, Schedule(id=1))
scheduler.schedule_task(feeding, event_morning, Schedule(id=1))
scheduler.schedule_task(bath,    event_noon,    Schedule(id=2))
scheduler.schedule_task(brush,   event_morning, Schedule(id=1))
scheduler.schedule_task(play,    event_noon,    Schedule(id=2))
scheduler.schedule_task(meds,    event_evening, Schedule(id=3))

schedule = Schedule(id=10)
schedule.add_event(event_morning)
schedule.add_event(event_noon)
schedule.add_event(event_evening)
scheduler.add_schedule(schedule)

# Print today's schedule
print("\nToday's Schedule")
print("=" * 40)
upcoming = scheduler.get_upcoming_tasks(owner, window=1)
for event in sorted(schedule.get_events(), key=lambda e: e.datetime):
    time_str = event.get_time()
    print(f"\n{time_str}")
    for task in event.get_tasks():
        pet_name = next((p.name for p in owner.pets if p.id == task.pet_id), "Unknown")
        print(f"  [{pet_name}] {task.get_name()} ({task.get_duration()} min) — {task.get_priority()} priority")
print("\nHave a great day!\n")
