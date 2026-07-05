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
        """Return the medication name."""
        return self.name

    def get_dosage(self) -> str:
        """Return the dosage string."""
        return self.dosage

    def get_frequency(self) -> str:
        """Return the administration frequency."""
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
        """Return the task name."""
        return self.name

    def get_type(self) -> str:
        """Return the task type (e.g. exercise, feeding, grooming)."""
        return self.type

    def get_duration(self) -> int:
        """Return the estimated duration in minutes."""
        return self.duration

    def set_duration(self, duration: int) -> None:
        """Set the estimated duration in minutes."""
        self.duration = duration

    def get_priority(self) -> str:
        """Return the task priority level."""
        return self.priority

    def set_priority(self, priority: str) -> None:
        """Set the task priority level."""
        self.priority = priority

    def get_description(self) -> str:
        """Return the task description."""
        return self.description

    def set_description(self, description: str) -> None:
        """Set the task description."""
        self.description = description

    def get_status(self) -> str:
        """Return the current task status."""
        return self.status

    def set_status(self, status: str) -> None:
        """Set the task status."""
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
        """Return the pet's name."""
        return self.name

    def get_type(self) -> str:
        """Return the pet's species type (e.g. Dog, Cat)."""
        return self.type

    def get_breed(self) -> str:
        """Return the pet's breed."""
        return self.breed

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet and set its pet_id back-reference."""
        task.pet_id = self.id
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet and clear its pet_id."""
        self.tasks.remove(task)
        task.pet_id = None

    def get_medications(self) -> List[Medication]:
        """Return all medications assigned to this pet."""
        return self.medications

    def add_medication(self, med: Medication) -> None:
        """Add a medication to this pet's medication list."""
        self.medications.append(med)

    def remove_medication(self, med: Medication) -> None:
        """Remove a medication from this pet's medication list."""
        self.medications.remove(med)


@dataclass
class Event:
    id: int
    datetime: str
    tasks: List[Task] = field(default_factory=list)

    def get_date(self) -> str:
        """Return the date portion of the event's datetime string."""
        return self.datetime.split("T")[0] if "T" in self.datetime else self.datetime.split(" ")[0]

    def get_time(self) -> str:
        """Return the time portion of the event's datetime string."""
        parts = self.datetime.split("T") if "T" in self.datetime else self.datetime.split(" ")
        return parts[1] if len(parts) > 1 else ""

    def get_tasks(self) -> List[Task]:
        """Return all tasks scheduled for this event."""
        return self.tasks

    def add_task(self, task: Task) -> None:
        """Add a task to this event."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this event."""
        self.tasks.remove(task)


@dataclass
class Schedule:
    id: int
    events: List[Event] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        """Add an event to this schedule."""
        self.events.append(event)

    def remove_event(self, event: Event) -> None:
        """Remove an event from this schedule."""
        self.events.remove(event)

    def get_events(self) -> List[Event]:
        """Return all events in this schedule."""
        return self.events


@dataclass
class Scheduler:
    id: int
    schedules: List[Schedule] = field(default_factory=list)

    def get_tasks_by_pet(self, pet: Pet) -> List[Task]:
        """Return all tasks assigned to a specific pet."""
        return list(pet.tasks)

    def get_tasks_by_owner(self, owner: Owner) -> List[Task]:
        """Return all tasks across every pet owned by the given owner."""
        return [task for pet in owner.pets for task in pet.tasks]

    def get_tasks_by_status(self, owner: Owner, status: str) -> List[Task]:
        """Return all of an owner's tasks that match the given status."""
        return [t for t in self.get_tasks_by_owner(owner) if t.status == status]

    def get_tasks_by_priority(self, owner: Owner, priority: str) -> List[Task]:
        """Return all of an owner's tasks that match the given priority level."""
        return [t for t in self.get_tasks_by_owner(owner) if t.priority == priority]

    def get_upcoming_tasks(self, owner: Owner, window: int) -> List[Task]:
        """Return owner's tasks scheduled within the next `window` days."""
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
        """Set the task's status to 'complete'."""
        task.status = "complete"

    def reassign_task(self, task: Task, pet: Pet) -> None:
        """Move a task to a new pet; caller must remove it from the old pet first."""
        task.pet_id = pet.id
        if task not in pet.tasks:
            pet.tasks.append(task)

    def add_schedule(self, schedule: Schedule) -> None:
        """Add a schedule to this scheduler."""
        self.schedules.append(schedule)

    def remove_schedule(self, schedule: Schedule) -> None:
        """Remove a schedule from this scheduler."""
        self.schedules.remove(schedule)

    def get_schedules(self) -> List[Schedule]:
        """Return all schedules managed by this scheduler."""
        return self.schedules

    def get_schedule(self, schedule_id: int) -> Schedule | None:
        """Return the schedule with the given id, or None if not found."""
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                return schedule
        return None

    def schedule_task(self, task: Task, event: Event, schedule: Schedule) -> None:
        """Add a task to an event and ensure that event belongs to the schedule."""
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
        """Return the owner's name."""
        return self.name

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pet list."""
        self.pets.remove(pet)
