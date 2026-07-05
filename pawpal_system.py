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
        pass

    def get_dosage(self) -> str:
        pass

    def get_frequency(self) -> str:
        pass


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
        pass

    def get_type(self) -> str:
        pass

    def get_duration(self) -> int:
        pass

    def set_duration(self, duration: int) -> None:
        pass

    def get_priority(self) -> str:
        pass

    def set_priority(self, priority: str) -> None:
        pass

    def get_description(self) -> str:
        pass

    def set_description(self, description: str) -> None:
        pass

    def get_status(self) -> str:
        pass

    def set_status(self, status: str) -> None:
        pass


@dataclass
class Pet:
    name: str
    id: int
    type: str
    breed: str
    tasks: List[Task] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)

    def get_name(self) -> str:
        pass

    def get_type(self) -> str:
        pass

    def get_breed(self) -> str:
        pass

    def get_tasks(self) -> List[Task]:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_medications(self) -> List[Medication]:
        pass

    def add_medication(self, med: Medication) -> None:
        pass

    def remove_medication(self, med: Medication) -> None:
        pass


@dataclass
class Event:
    id: int
    datetime: str
    tasks: List[Task] = field(default_factory=list)

    def get_date(self) -> str:
        pass

    def get_time(self) -> str:
        pass

    def get_tasks(self) -> List[Task]:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass


@dataclass
class Schedule:
    id: int
    events: List[Event] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        pass

    def remove_event(self, event: Event) -> None:
        pass

    def get_events(self) -> List[Event]:
        pass


@dataclass
class Scheduler:
    id: int
    schedules: List[Schedule] = field(default_factory=list)

    def get_tasks_by_pet(self, pet: Pet) -> List[Task]:
        pass

    def get_tasks_by_owner(self, owner: Owner) -> List[Task]:
        pass

    def get_tasks_by_status(self, owner: Owner, status: str) -> List[Task]:
        pass

    def get_tasks_by_priority(self, owner: Owner, priority: str) -> List[Task]:
        pass

    def get_upcoming_tasks(self, owner: Owner, window: int) -> List[Task]:
        pass

    def mark_task_complete(self, task: Task) -> None:
        pass

    def reassign_task(self, task: Task, pet: Pet) -> None:
        pass

    def add_schedule(self, schedule: Schedule) -> None:
        pass

    def remove_schedule(self, schedule: Schedule) -> None:
        pass

    def get_schedules(self) -> List[Schedule]:
        pass

    def get_schedule(self, schedule_id: int) -> Schedule | None:
        pass

    def schedule_task(self, task: Task, event: Event, schedule: Schedule) -> None:
        pass


@dataclass
class Owner:
    name: str
    id: int
    pets: List[Pet] = field(default_factory=list)
    scheduler: Scheduler = field(default_factory=lambda: Scheduler(id=0))

    def get_name(self) -> str:
        pass

    def get_pets(self) -> List[Pet]:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass
