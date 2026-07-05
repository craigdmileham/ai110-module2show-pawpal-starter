from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Event, Schedule


def make_task(id=1, status="pending", priority="medium"):
    return Task(name="Test Task", id=id, type="exercise", duration=15,
                recurring=False, priority=priority, description="desc", status=status)

def make_pet(id=1):
    return Pet(name="Buddy", id=id, species="Dog", breed="Labrador")

def make_owner():
    scheduler = Scheduler(id=1)
    owner = Owner(name="Alex", id=1, scheduler=scheduler)
    return owner, scheduler


# --- Task tests ---

def test_mark_task_complete_changes_status():
    task = make_task()
    scheduler = Scheduler(id=1)
    scheduler.mark_task_complete(task)
    assert task.get_status() == "complete"

def test_mark_task_complete_does_not_affect_other_fields():
    task = make_task()
    scheduler = Scheduler(id=1)
    scheduler.mark_task_complete(task)
    assert task.get_name() == "Test Task"
    assert task.get_priority() == "medium"


# --- Pet task count tests ---

def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task(id=1))
    assert len(pet.get_tasks()) == 1

def test_add_multiple_tasks_increases_pet_task_count():
    pet = make_pet()
    pet.add_task(make_task(id=1))
    pet.add_task(make_task(id=2))
    pet.add_task(make_task(id=3))
    assert len(pet.get_tasks()) == 3

def test_remove_task_decreases_pet_task_count():
    pet = make_pet()
    task = make_task()
    pet.add_task(task)
    pet.remove_task(task)
    assert len(pet.get_tasks()) == 0


# --- Scheduler filter tests ---

def test_get_tasks_by_pet_returns_correct_tasks():
    pet = make_pet()
    task = make_task()
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    assert task in scheduler.get_tasks_by_pet(pet)

def test_get_tasks_by_owner_aggregates_across_pets():
    owner, scheduler = make_owner()
    pet1 = make_pet(id=1)
    pet2 = make_pet(id=2)
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    pet1.add_task(t1)
    pet2.add_task(t2)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    result = scheduler.get_tasks_by_owner(owner)
    assert t1 in result and t2 in result

def test_get_tasks_by_status_filters_correctly():
    owner, scheduler = make_owner()
    pet = make_pet()
    owner.add_pet(pet)
    t_done = make_task(id=1, status="complete")
    t_pending = make_task(id=2, status="pending")
    pet.add_task(t_done)
    pet.add_task(t_pending)
    result = scheduler.get_tasks_by_status(owner, "complete")
    assert t_done in result
    assert t_pending not in result

def test_get_tasks_by_priority_filters_correctly():
    owner, scheduler = make_owner()
    pet = make_pet()
    owner.add_pet(pet)
    t_high = make_task(id=1, priority="high")
    t_low  = make_task(id=2, priority="low")
    pet.add_task(t_high)
    pet.add_task(t_low)
    result = scheduler.get_tasks_by_priority(owner, "high")
    assert t_high in result
    assert t_low not in result


# --- Reassign task tests ---

def test_reassign_task_updates_pet_id():
    pet1 = make_pet(id=1)
    pet2 = make_pet(id=2)
    task = make_task()
    pet1.add_task(task)
    scheduler = Scheduler(id=1)
    pet1.remove_task(task)
    scheduler.reassign_task(task, pet2)
    assert task.pet_id == pet2.id
    assert task in pet2.get_tasks()


# --- Recurring task tests ---

def make_recurring_task(id=99, frequency="daily"):
    return Task(name="Walk", id=id, type="exercise", duration=30,
                recurring=True, frequency=frequency, priority="high",
                description="walk", status="pending")


def test_mark_complete_nonrecurring_returns_none():
    task = make_task()  # frequency=None by default
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    result = scheduler.mark_task_complete(task, schedule=schedule)
    assert result is None

def test_mark_complete_recurring_no_schedule_returns_none():
    task = make_recurring_task(id=100)
    scheduler = Scheduler(id=1)
    result = scheduler.mark_task_complete(task)
    assert result is None

def test_mark_complete_daily_creates_new_task():
    pet = make_pet(id=1)
    task = make_recurring_task(id=101, frequency="daily")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    new_task = scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    assert new_task is not None
    assert new_task.status == "pending"
    assert new_task.pet_id == pet.id
    assert new_task.name == task.name
    assert new_task.frequency == "daily"

def test_mark_complete_daily_scheduled_tomorrow():
    pet = make_pet(id=1)
    task = make_recurring_task(id=102, frequency="daily")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    new_task = scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    event = next(
        (e for s in scheduler.schedules for e in s.events if new_task in e.tasks),
        None,
    )
    assert event is not None
    assert datetime.fromisoformat(event.datetime).date() == tomorrow

def test_mark_complete_weekly_scheduled_in_7_days():
    pet = make_pet(id=1)
    task = make_recurring_task(id=103, frequency="weekly")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    new_task = scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    in_7_days = (datetime.now() + timedelta(days=7)).date()
    event = next(
        (e for s in scheduler.schedules for e in s.events if new_task in e.tasks),
        None,
    )
    assert event is not None
    assert datetime.fromisoformat(event.datetime).date() == in_7_days

# --- Conflict detection tests ---

def test_schedule_task_no_conflict_returns_none():
    pet = make_pet(id=1)
    task = make_task(id=1)
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    event = Event(id=1, datetime="2026-07-05T07:00:00")
    result = scheduler.schedule_task(task, event, schedule, pets=[pet])
    assert result is None

def test_schedule_task_same_pet_conflict_returns_warning():
    pet = make_pet(id=1)
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    event = Event(id=1, datetime="2026-07-05T07:00:00")
    scheduler.schedule_task(t1, event, schedule, pets=[pet])
    warning = scheduler.schedule_task(t2, event, schedule, pets=[pet])
    assert warning is not None
    assert "[WARNING]" in warning
    assert "Same-pet" in warning
    assert "Buddy" in warning

def test_schedule_task_cross_pet_conflict_returns_warning():
    pet1 = make_pet(id=1)
    pet2 = Pet(name="Whiskers", id=2, species="Cat")
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    pet1.add_task(t1)
    pet2.add_task(t2)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    event = Event(id=1, datetime="2026-07-05T07:00:00")
    scheduler.schedule_task(t1, event, schedule, pets=[pet1, pet2])
    warning = scheduler.schedule_task(t2, event, schedule, pets=[pet1, pet2])
    assert warning is not None
    assert "[WARNING]" in warning
    assert "Cross-pet" in warning
    assert "Buddy" in warning
    assert "Whiskers" in warning

def test_schedule_task_warning_includes_task_names():
    pet = make_pet(id=1)
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    event = Event(id=1, datetime="2026-07-05T09:00:00")
    scheduler.schedule_task(t1, event, schedule, pets=[pet])
    warning = scheduler.schedule_task(t2, event, schedule, pets=[pet])
    assert "Test Task" in warning


def test_mark_complete_does_not_change_original_task_fields():
    pet = make_pet(id=1)
    task = make_recurring_task(id=104, frequency="daily")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    assert task.name == "Walk"
    assert task.type == "exercise"
    assert task.priority == "high"
    assert task.status == "complete"
    assert task.pet_id == pet.id


# --- Sorting correctness tests ---

def make_event_task(task_id, event_datetime, schedule, scheduler, pet):
    task = Task(name=f"Task {task_id}", id=task_id, type="exercise", duration=15,
                recurring=False, priority="medium", description="desc", status="pending")
    pet.add_task(task)
    event = Event(id=task_id, datetime=event_datetime)
    scheduler.schedule_task(task, event, schedule, pets=[pet])
    return task


def test_get_events_sort_returns_chronological_order():
    schedule = Schedule(id=1)
    e1 = Event(id=1, datetime="2026-07-05T09:00:00")
    e2 = Event(id=2, datetime="2026-07-05T07:00:00")
    e3 = Event(id=3, datetime="2026-07-05T11:00:00")
    schedule.add_event(e1)
    schedule.add_event(e2)
    schedule.add_event(e3)
    sorted_events = schedule.get_events(sort=True)
    datetimes = [e.datetime for e in sorted_events]
    assert datetimes == sorted(datetimes)


def test_sort_by_time_returns_tasks_in_time_order():
    pet = make_pet(id=1)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    t_noon = make_event_task(201, "2026-07-05T12:00:00", schedule, scheduler, pet)
    t_morning = make_event_task(202, "2026-07-05T06:00:00", schedule, scheduler, pet)
    t_evening = make_event_task(203, "2026-07-05T18:00:00", schedule, scheduler, pet)
    sorted_tasks = scheduler.sort_by_time([t_noon, t_morning, t_evening])
    assert sorted_tasks == [t_morning, t_noon, t_evening]


def test_sort_by_time_unscheduled_tasks_go_last():
    pet = make_pet(id=1)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    t_early = make_event_task(204, "2026-07-05T08:00:00", schedule, scheduler, pet)
    t_unscheduled = Task(name="Floating Task", id=205, type="grooming", duration=20,
                         recurring=False, priority="low", description="no event", status="pending")
    pet.add_task(t_unscheduled)
    sorted_tasks = scheduler.sort_by_time([t_unscheduled, t_early])
    assert sorted_tasks[0] is t_early
    assert sorted_tasks[-1] is t_unscheduled


def test_sort_by_time_stable_across_same_time():
    pet = make_pet(id=1)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    event = Event(id=1, datetime="2026-07-05T10:00:00")
    t1 = Task(name="A", id=206, type="exercise", duration=10, recurring=False,
              priority="high", description="d", status="pending")
    t2 = Task(name="B", id=207, type="exercise", duration=10, recurring=False,
              priority="high", description="d", status="pending")
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler.schedule_task(t1, event, schedule, pets=[pet])
    scheduler.schedule_task(t2, event, schedule, pets=[pet])
    sorted_tasks = scheduler.sort_by_time([t1, t2])
    assert len(sorted_tasks) == 2
    assert t1 in sorted_tasks and t2 in sorted_tasks


# --- Recurrence logic tests ---

def test_mark_complete_daily_new_task_is_added_to_pet():
    pet = make_pet(id=1)
    task = make_recurring_task(id=110, frequency="daily")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    before_count = len(pet.get_tasks())
    new_task = scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    assert len(pet.get_tasks()) == before_count + 1
    assert new_task in pet.get_tasks()


def test_mark_complete_daily_new_task_inherits_type_and_duration():
    pet = make_pet(id=1)
    task = make_recurring_task(id=111, frequency="daily")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    new_task = scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    assert new_task.type == task.type
    assert new_task.duration == task.duration
    assert new_task.description == task.description


def test_mark_complete_daily_new_event_added_to_schedule():
    pet = make_pet(id=1)
    task = make_recurring_task(id=112, frequency="daily")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    assert len(schedule.get_events()) == 1


def test_mark_complete_recurring_original_marked_complete():
    pet = make_pet(id=1)
    task = make_recurring_task(id=113, frequency="daily")
    pet.add_task(task)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    scheduler.add_schedule(schedule)
    scheduler.mark_task_complete(task, schedule=schedule, pet=pet)
    assert task.status == "complete"


# --- Conflict detection tests (additional coverage) ---

def test_no_conflict_when_different_event_times():
    pet = make_pet(id=1)
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    e1 = Event(id=1, datetime="2026-07-05T07:00:00")
    e2 = Event(id=2, datetime="2026-07-05T09:00:00")
    w1 = scheduler.schedule_task(t1, e1, schedule, pets=[pet])
    w2 = scheduler.schedule_task(t2, e2, schedule, pets=[pet])
    assert w1 is None
    assert w2 is None


def test_conflict_warning_contains_event_datetime():
    pet = make_pet(id=1)
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    event = Event(id=1, datetime="2026-07-05T08:30:00")
    scheduler.schedule_task(t1, event, schedule, pets=[pet])
    warning = scheduler.schedule_task(t2, event, schedule, pets=[pet])
    assert "2026-07-05T08:30:00" in warning


def test_conflict_task_still_added_despite_warning():
    pet = make_pet(id=1)
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    event = Event(id=1, datetime="2026-07-05T07:00:00")
    scheduler.schedule_task(t1, event, schedule, pets=[pet])
    scheduler.schedule_task(t2, event, schedule, pets=[pet])
    assert t2 in event.get_tasks()


def test_three_tasks_same_event_generates_conflict_for_second_and_third():
    pet = make_pet(id=1)
    t1 = make_task(id=1)
    t2 = make_task(id=2)
    t3 = make_task(id=3)
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    scheduler = Scheduler(id=1)
    schedule = Schedule(id=1)
    event = Event(id=1, datetime="2026-07-05T10:00:00")
    w1 = scheduler.schedule_task(t1, event, schedule, pets=[pet])
    w2 = scheduler.schedule_task(t2, event, schedule, pets=[pet])
    w3 = scheduler.schedule_task(t3, event, schedule, pets=[pet])
    assert w1 is None
    assert w2 is not None
    assert w3 is not None
