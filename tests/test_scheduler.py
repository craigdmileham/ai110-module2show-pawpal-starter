from datetime import datetime, timedelta

import pytest

from models import Event, Owner, Pet, Schedule, Task
from scheduler import ScheduleConflictError, Scheduler


def make_scheduler_with_owner():
    scheduler = Scheduler()
    owner = Owner(name="Jordan")
    scheduler.addSchedule(owner.getSchedule())
    return scheduler, owner


def test_schedule_no_conflict():
    scheduler, owner = make_scheduler_with_owner()
    t1 = Task(name="Walk", type="exercise", duration=30)
    t2 = Task(name="Feed", type="feeding", duration=10)
    e1 = Event(datetime=datetime(2026, 7, 4, 8, 0))
    e2 = Event(datetime=datetime(2026, 7, 4, 9, 0))
    scheduler.scheduleTask(t1, e1, owner.getSchedule())
    scheduler.scheduleTask(t2, e2, owner.getSchedule())
    assert len(owner.getSchedule().getEvents()) == 2


def test_schedule_conflict_raises():
    scheduler, owner = make_scheduler_with_owner()
    t1 = Task(name="Walk", type="exercise", duration=60)
    t2 = Task(name="Feed", type="feeding", duration=10)
    e1 = Event(datetime=datetime(2026, 7, 4, 8, 0))
    e2 = Event(datetime=datetime(2026, 7, 4, 8, 30))  # overlaps with e1 (8:00–9:00)
    scheduler.scheduleTask(t1, e1, owner.getSchedule())
    with pytest.raises(ScheduleConflictError):
        scheduler.scheduleTask(t2, e2, owner.getSchedule())


def test_conflict_task_not_added_on_conflict():
    scheduler, owner = make_scheduler_with_owner()
    t1 = Task(name="Walk", type="exercise", duration=60)
    t2 = Task(name="Feed", type="feeding", duration=10)
    e1 = Event(datetime=datetime(2026, 7, 4, 8, 0))
    e2 = Event(datetime=datetime(2026, 7, 4, 8, 30))
    scheduler.scheduleTask(t1, e1, owner.getSchedule())
    try:
        scheduler.scheduleTask(t2, e2, owner.getSchedule())
    except ScheduleConflictError:
        pass
    # e2 should not be in schedule, t2 should not be in e2
    assert e2 not in owner.getSchedule().getEvents()
    assert len(e2.getTasks()) == 0


def test_recurring_daily_generates_events():
    scheduler, owner = make_scheduler_with_owner()
    task = Task(name="Walk", type="exercise", duration=30, recurring=True, frequency="Daily")
    base_event = Event(datetime=datetime(2026, 7, 4, 8, 0))
    scheduler.scheduleTask(task, base_event, owner.getSchedule())
    events = owner.getSchedule().getEvents()
    # base event + 7 recurring = 8 total
    assert len(events) == 8


def test_recurring_weekly_events_spaced_7_days():
    scheduler, owner = make_scheduler_with_owner()
    task = Task(name="Groom", type="grooming", duration=15, recurring=True, frequency="Weekly")
    base_dt = datetime(2026, 7, 4, 10, 0)
    base_event = Event(datetime=base_dt)
    scheduler.scheduleTask(task, base_event, owner.getSchedule())
    events = sorted(owner.getSchedule().getEvents(), key=lambda e: e.datetime)
    # check consecutive events are 7 days apart
    for i in range(1, len(events)):
        diff = events[i].datetime - events[i - 1].datetime
        assert diff == timedelta(weeks=1)


def test_mark_task_complete():
    scheduler, owner = make_scheduler_with_owner()
    task = Task(name="Walk", type="exercise", duration=30)
    scheduler.markTaskComplete(task)
    assert task.getStatus() == "complete"


def test_get_tasks_by_priority():
    scheduler, owner = make_scheduler_with_owner()
    t_high = Task(name="Walk", type="exercise", duration=30, priority="high")
    t_low = Task(name="Trim nails", type="grooming", duration=10, priority="low")
    e1 = Event(datetime=datetime(2026, 7, 4, 8, 0))
    e2 = Event(datetime=datetime(2026, 7, 4, 9, 0))
    scheduler.scheduleTask(t_high, e1, owner.getSchedule())
    scheduler.scheduleTask(t_low, e2, owner.getSchedule())
    high_tasks = scheduler.getTasksByPriority("high")
    assert any(t.getName() == "Walk" for t in high_tasks)
    assert not any(t.getName() == "Trim nails" for t in high_tasks)


def test_get_upcoming_tasks_sorted_by_priority():
    scheduler, owner = make_scheduler_with_owner()
    future = datetime.now() + timedelta(hours=1)
    t_low = Task(name="Trim nails", type="grooming", duration=10, priority="low")
    t_high = Task(name="Walk", type="exercise", duration=30, priority="high")
    e1 = Event(datetime=future)
    e2 = Event(datetime=future + timedelta(hours=1))
    scheduler.scheduleTask(t_low, e1, owner.getSchedule())
    scheduler.scheduleTask(t_high, e2, owner.getSchedule())
    upcoming = scheduler.getUpcomingTasks(owner)
    assert upcoming[0].getPriority() == "high"
    assert upcoming[-1].getPriority() == "low"


def test_get_upcoming_excludes_completed():
    scheduler, owner = make_scheduler_with_owner()
    future = datetime.now() + timedelta(hours=1)
    task = Task(name="Walk", type="exercise", duration=30)
    event = Event(datetime=future)
    scheduler.scheduleTask(task, event, owner.getSchedule())
    scheduler.markTaskComplete(task)
    upcoming = scheduler.getUpcomingTasks(owner)
    assert not any(t.getName() == "Walk" for t in upcoming)


def test_reassign_task():
    scheduler, owner = make_scheduler_with_owner()
    luna = Pet(name="Luna", species="dog")
    milo = Pet(name="Milo", species="cat")
    owner.addPet(luna)
    owner.addPet(milo)
    task = Task(name="Groom", type="grooming", duration=15)
    luna.addTask(task)
    assert len(luna.getTasks()) == 1
    scheduler.reassignTask(task, milo)
    assert len(milo.getTasks()) == 1


def test_get_tasks_by_status():
    scheduler, owner = make_scheduler_with_owner()
    t1 = Task(name="Walk", type="exercise", duration=30)
    t2 = Task(name="Feed", type="feeding", duration=10)
    e1 = Event(datetime=datetime(2026, 7, 4, 8, 0))
    e2 = Event(datetime=datetime(2026, 7, 4, 9, 0))
    scheduler.scheduleTask(t1, e1, owner.getSchedule())
    scheduler.scheduleTask(t2, e2, owner.getSchedule())
    scheduler.markTaskComplete(t1)
    complete = scheduler.getTasksByStatus("complete")
    pending = scheduler.getTasksByStatus("pending")
    assert any(t.getName() == "Walk" for t in complete)
    assert any(t.getName() == "Feed" for t in pending)
