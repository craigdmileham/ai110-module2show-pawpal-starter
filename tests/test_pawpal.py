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
