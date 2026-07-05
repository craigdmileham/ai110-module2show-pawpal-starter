from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Medication:
    name: str
    id: int
    dosage: str
    frequency: str
    events: List["Event"] = field(default_factory=list)  # scheduled reminder events

    def get_name(self) -> str:
        return self.name

    def get_dosage(self) -> str:
        return self.dosage

    def get_frequency(self) -> str:
        return self.frequency


@dataclass
class Task:
    name: str
    id: int
    type: str
    duration: int
    recurring: bool
    priority: str
    description: str
    status: str
    pet_id: int | None = None  # back-reference so reassign_task can find current owner

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return self.type

    def get_duration(self) -> int:
        return self.duration

    def set_duration(self, duration: int) -> None:
        self.duration = duration

    def get_priority(self) -> str:
        return self.priority

    def set_priority(self, priority: str) -> None:
        self.priority = priority

    def get_description(self) -> str:
        return self.description

    def set_description(self, description: str) -> None:
        self.description = description

    def get_status(self) -> str:
        return self.status

    def set_status(self, status: str) -> None:
        self.status = status


@dataclass
class Pet:
    name: str
    id: int
    type: str
    breed: str
    tasks: List[Task] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return self.type

    def get_breed(self) -> str:
        return self.breed

    def get_tasks(self) -> List[Task]:
        return self.tasks

    def add_task(self, task: Task) -> None:
        task.pet_id = self.id
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)
        task.pet_id = None

    def get_medications(self) -> List[Medication]:
        return self.medications

    def add_medication(self, med: Medication) -> None:
        self.medications.append(med)

    def remove_medication(self, med: Medication) -> None:
        self.medications.remove(med)


@dataclass
class Event:
    id: int
    datetime: str
    tasks: List[Task] = field(default_factory=list)

    def get_date(self) -> str:
        return self.datetime.split("T")[0] if "T" in self.datetime else self.datetime.split(" ")[0]

    def get_time(self) -> str:
        parts = self.datetime.split("T") if "T" in self.datetime else self.datetime.split(" ")
        return parts[1] if len(parts) > 1 else ""

    def get_tasks(self) -> List[Task]:
        return self.tasks

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)


@dataclass
class Schedule:
    id: int
    events: List[Event] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def remove_event(self, event: Event) -> None:
        self.events.remove(event)

    def get_events(self) -> List[Event]:
        return self.events


@dataclass
class Scheduler:
    id: int
    schedules: List[Schedule] = field(default_factory=list)

    def get_tasks_by_pet(self, pet: Pet) -> List[Task]:
        return list(pet.tasks)

    def get_tasks_by_owner(self, owner: Owner) -> List[Task]:
        return [task for pet in owner.pets for task in pet.tasks]

    def get_tasks_by_status(self, owner: Owner, status: str) -> List[Task]:
        return [t for t in self.get_tasks_by_owner(owner) if t.status == status]

    def get_tasks_by_priority(self, owner: Owner, priority: str) -> List[Task]:
        return [t for t in self.get_tasks_by_owner(owner) if t.priority == priority]

    def get_upcoming_tasks(self, owner: Owner, window: int) -> List[Task]:
        # Returns tasks scheduled within `window` next events across all schedules
        from datetime import datetime, timedelta
        now = datetime.now()
        cutoff = now + timedelta(days=window)
        owner_task_ids = {id(t) for t in self.get_tasks_by_owner(owner)}
        upcoming = []
        seen = set()
        for schedule in self.schedules:
            for event in schedule.events:
                try:
                    event_dt = datetime.fromisoformat(event.datetime)
                except ValueError:
                    continue
                if now <= event_dt <= cutoff:
                    for task in event.tasks:
                        if id(task) in owner_task_ids and id(task) not in seen:
                            upcoming.append(task)
                            seen.add(id(task))
        return upcoming

    def mark_task_complete(self, task: Task) -> None:
        task.status = "complete"

    def reassign_task(self, task: Task, pet: Pet) -> None:
        # Caller removes task from old pet; this updates ownership and adds to new pet
        task.pet_id = pet.id
        if task not in pet.tasks:
            pet.tasks.append(task)

    def add_schedule(self, schedule: Schedule) -> None:
        self.schedules.append(schedule)

    def remove_schedule(self, schedule: Schedule) -> None:
        self.schedules.remove(schedule)

    def get_schedules(self) -> List[Schedule]:
        return self.schedules

    def get_schedule(self, schedule_id: int) -> Schedule | None:
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                return schedule
        return None

    def schedule_task(self, task: Task, event: Event, schedule: Schedule) -> None:
        event.add_task(task)
        if event not in schedule.events:
            schedule.add_event(event)


@dataclass
class Owner:
    name: str
    id: int
    pets: List[Pet] = field(default_factory=list)
    scheduler: Scheduler = field(default_factory=lambda: Scheduler(id=0))

    def get_name(self) -> str:
        return self.name

    def get_pets(self) -> List[Pet]:
        return self.pets

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        self.pets.remove(pet)
