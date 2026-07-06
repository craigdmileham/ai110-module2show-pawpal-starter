from __future__ import annotations

from datetime import datetime

from pawpal_system import Event, Medication, Owner, Pet, Task, Schedule, Scheduler


def load_dummy_data() -> tuple[Owner, Scheduler]:
    scheduler = Scheduler()
    schedule = Schedule()
    scheduler.add_schedule(schedule)

    jordan = Owner(name="Jordan")

    luna = Pet(name="Luna", species="dog", breed="Golden Retriever")
    milo = Pet(name="Milo", species="cat", breed="Tabby")
    jordan.add_pet(luna)
    jordan.add_pet(milo)

    # Luna's tasks
    walk = Task(
        name="Morning Walk",
        type="exercise",
        duration=30,
        priority="high",
        recurring=True,
        frequency="daily",
        description="30-minute walk around the neighborhood",
        status="pending",
    )
    feeding_luna = Task(
        name="Luna's Dinner",
        type="feeding",
        duration=10,
        priority="high",
        recurring=True,
        frequency="daily",
        description="Measure and serve Luna's evening meal",
        status="pending",
    )
    luna.add_task(walk)
    luna.add_task(feeding_luna)

    # Milo's tasks
    brush = Task(
        name="Brush Fur",
        type="grooming",
        duration=15,
        priority="medium",
        recurring=True,
        frequency="weekly",
        description="Brush Milo's coat to prevent matting",
        status="pending",
    )
    feeding_milo = Task(
        name="Milo's Dinner",
        type="feeding",
        duration=5,
        priority="high",
        recurring=True,
        frequency="daily",
        description="Serve Milo's evening meal",
        status="pending",
    )
    milo.add_task(brush)
    milo.add_task(feeding_milo)

    # Milo's medication
    allergy_med = Medication(
        name="Apoquel",
        dosage="5.4mg",
        frequency="once daily",
    )
    milo.add_medication(allergy_med)

    # Schedule tasks for today
    today = datetime.now().replace(second=0, microsecond=0)
    eight_am = today.replace(hour=8, minute=0)
    six_pm = today.replace(hour=18, minute=0)
    ten_am = today.replace(hour=10, minute=0)

    all_pets = [luna, milo]
    scheduler.schedule_task(walk, Event(datetime=eight_am.isoformat()), schedule, pets=all_pets)
    scheduler.schedule_task(feeding_luna, Event(datetime=six_pm.isoformat()), schedule, pets=all_pets)
    scheduler.schedule_task(feeding_milo, Event(datetime=six_pm.replace(minute=15).isoformat()), schedule, pets=all_pets)
    scheduler.schedule_task(brush, Event(datetime=ten_am.isoformat()), schedule, pets=all_pets)

    return jordan, scheduler
