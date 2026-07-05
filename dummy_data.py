from __future__ import annotations

from datetime import datetime

from models import Event, Medication, Owner, Pet, Task
from scheduler import Scheduler, ScheduleConflictError


def load_dummy_data() -> tuple[Owner, Scheduler]:
    scheduler = Scheduler()

    jordan = Owner(name="Jordan")
    scheduler.addSchedule(jordan.getSchedule())

    luna = Pet(name="Luna", species="dog", breed="Golden Retriever")
    milo = Pet(name="Milo", species="cat", breed="Tabby")
    jordan.addPet(luna)
    jordan.addPet(milo)

    # Luna's tasks
    walk = Task(
        name="Morning Walk",
        type="exercise",
        duration=30,
        priority="high",
        recurring=True,
        frequency="Daily",
        description="30-minute walk around the neighborhood",
    )
    feeding_luna = Task(
        name="Luna's Dinner",
        type="feeding",
        duration=10,
        priority="high",
        recurring=True,
        frequency="Daily",
        description="Measure and serve Luna's evening meal",
    )
    luna.addTask(walk)
    luna.addTask(feeding_luna)

    # Milo's tasks
    brush = Task(
        name="Brush Fur",
        type="grooming",
        duration=15,
        priority="medium",
        recurring=True,
        frequency="Weekly",
        description="Brush Milo's coat to prevent matting",
    )
    feeding_milo = Task(
        name="Milo's Dinner",
        type="feeding",
        duration=5,
        priority="high",
        recurring=True,
        frequency="Daily",
        description="Serve Milo's evening meal",
    )
    milo.addTask(brush)
    milo.addTask(feeding_milo)

    # Milo's medication
    allergy_med = Medication(
        name="Apoquel",
        dosage="5.4mg",
        frequency="once daily",
    )
    milo.addMedication(allergy_med)

    # Schedule tasks starting today
    today = datetime.now().replace(second=0, microsecond=0)
    eight_am = today.replace(hour=8, minute=0)
    six_pm = today.replace(hour=18, minute=0)
    ten_am = today.replace(hour=10, minute=0)

    try:
        scheduler.scheduleTask(walk, Event(datetime=eight_am), jordan.getSchedule())
    except ScheduleConflictError:
        pass

    try:
        scheduler.scheduleTask(feeding_luna, Event(datetime=six_pm), jordan.getSchedule())
    except ScheduleConflictError:
        pass

    try:
        scheduler.scheduleTask(feeding_milo, Event(datetime=six_pm.replace(minute=15)), jordan.getSchedule())
    except ScheduleConflictError:
        pass

    try:
        scheduler.scheduleTask(brush, Event(datetime=ten_am), jordan.getSchedule())
    except ScheduleConflictError:
        pass

    return jordan, scheduler
