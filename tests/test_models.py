from datetime import datetime, timedelta

import pytest

from models import Event, Medication, Owner, Pet, Schedule, Task


def test_owner_add_remove_pet():
    owner = Owner(name="Jordan")
    luna = Pet(name="Luna", species="dog")
    milo = Pet(name="Milo", species="cat")
    owner.addPet(luna)
    owner.addPet(milo)
    assert len(owner.getPets()) == 2
    owner.removePet(luna)
    assert len(owner.getPets()) == 1
    assert owner.getPets()[0].getName() == "Milo"


def test_owner_auto_creates_schedule():
    owner = Owner(name="Sam")
    assert owner.getSchedule() is not None
    assert isinstance(owner.getSchedule(), Schedule)


def test_pet_add_remove_task():
    pet = Pet(name="Luna", species="dog")
    task = Task(name="Walk", type="exercise", duration=30)
    pet.addTask(task)
    assert len(pet.getTasks()) == 1
    pet.removeTask(task)
    assert len(pet.getTasks()) == 0


def test_pet_add_remove_medication():
    pet = Pet(name="Milo", species="cat")
    med = Medication(name="Apoquel", dosage="5.4mg", frequency="once daily")
    pet.addMedication(med)
    assert len(pet.getMedications()) == 1
    pet.removeMedication(med)
    assert len(pet.getMedications()) == 0


def test_task_setters():
    task = Task(name="Walk", type="exercise", duration=30, priority="low")
    task.setDuration(45)
    assert task.getDuration() == 45
    task.setPriority("high")
    assert task.getPriority() == "high"
    task.setDescription("Daily walk")
    assert task.getDescription() == "Daily walk"
    task.setStatus("complete")
    assert task.getStatus() == "complete"


def test_task_default_status():
    task = Task(name="Feed", type="feeding", duration=10)
    assert task.getStatus() == "pending"


def test_event_end_time():
    dt = datetime(2026, 7, 4, 8, 0)
    t1 = Task(name="Walk", type="exercise", duration=15)
    t2 = Task(name="Feed", type="feeding", duration=15)
    event = Event(datetime=dt, tasks=[t1, t2])
    assert event.end_time == dt + timedelta(minutes=30)


def test_event_end_time_empty_tasks_floor():
    dt = datetime(2026, 7, 4, 8, 0)
    event = Event(datetime=dt)
    assert event.end_time == dt + timedelta(minutes=1)


def test_event_add_remove_task():
    dt = datetime(2026, 7, 4, 8, 0)
    event = Event(datetime=dt)
    task = Task(name="Walk", type="exercise", duration=20)
    event.addTask(task)
    assert len(event.getTasks()) == 1
    event.removeTask(task)
    assert len(event.getTasks()) == 0


def test_schedule_defensive_copy():
    schedule = Schedule()
    event = Event(datetime=datetime(2026, 7, 4, 9, 0))
    schedule.addEvent(event)
    copy = schedule.getEvents()
    copy.clear()
    assert len(schedule.getEvents()) == 1


def test_schedule_remove_event():
    schedule = Schedule()
    event = Event(datetime=datetime(2026, 7, 4, 9, 0))
    schedule.addEvent(event)
    schedule.removeEvent(event)
    assert len(schedule.getEvents()) == 0


def test_pet_get_tasks_returns_copy():
    pet = Pet(name="Luna", species="dog")
    task = Task(name="Walk", type="exercise", duration=30)
    pet.addTask(task)
    copy = pet.getTasks()
    copy.clear()
    assert len(pet.getTasks()) == 1


def test_medication_getters():
    med = Medication(name="Apoquel", dosage="5.4mg", frequency="once daily")
    assert med.getName() == "Apoquel"
    assert med.getDosage() == "5.4mg"
    assert med.getFrequency() == "once daily"
