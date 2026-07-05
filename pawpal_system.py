from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import itertools

_id_counter = itertools.count(1)

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _next_id() -> int:
    return next(_id_counter)


@dataclass
class Medication:
    name: str
    dosage: str
    frequency: str
    events: List["Event"] = field(default_factory=list)  # scheduled reminder events
    id: int = field(default_factory=_next_id)

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
    type: str
    duration: int
    recurring: bool
    priority: str
    description: str
    status: str
    frequency: str | None = None  # "daily" | "weekly" | None
    pet_id: int | None = None  # back-reference so reassign_task can find current owner
    id: int = field(default_factory=_next_id)

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
    species: str
    breed: str = None
    tasks: List[Task] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)
    id: int = field(default_factory=_next_id)

    def get_name(self) -> str:
        """Return the pet's name."""
        return self.name

    def get_species(self) -> str:
        """Return the pet's species type (e.g. Dog, Cat)."""
        return self.species

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
    datetime: str
    tasks: List[Task] = field(default_factory=list)
    id: int = field(default_factory=_next_id)

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
    events: List[Event] = field(default_factory=list)
    id: int = field(default_factory=_next_id)

    def add_event(self, event: Event) -> None:
        """Add an event to this schedule."""
        self.events.append(event)

    def remove_event(self, event: Event) -> None:
        """Remove an event from this schedule."""
        self.events.remove(event)

    def get_events(self, sort: bool = False) -> List[Event]:
        """Return all events in this schedule, optionally sorted by datetime."""
        if sort:
            return sorted(self.events, key=lambda e: e.datetime)
        return self.events


@dataclass
class Scheduler:
    schedules: List[Schedule] = field(default_factory=list)
    id: int = field(default_factory=_next_id)

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

    def get_tasks_by_pet_name(self, owner: Owner, pet_name: str) -> List[Task]:
        """Return all tasks assigned to the pet with the given name."""
        return [task for pet in owner.pets if pet.name == pet_name for task in pet.tasks]

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

    def mark_task_complete(
        self,
        task: Task,
        schedule: Schedule | None = None,
        pet: Pet | None = None,
    ) -> Task | None:
        """Set the task's status to 'complete'.

        If the task has a frequency ('daily' or 'weekly') and a schedule is
        provided, a new pending instance is created for the next occurrence,
        added to the pet (if provided), and scheduled into a new Event.
        Returns the new Task, or None if no recurrence was created.
        """
        from datetime import datetime, timedelta
        task.status = "complete"
        if task.frequency is None or schedule is None:
            return None
        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(days=7)
        new_dt = (
            datetime.now() + delta
        ).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        new_task = Task(
            name=task.name,
            type=task.type,
            duration=task.duration,
            recurring=task.recurring,
            frequency=task.frequency,
            priority=task.priority,
            description=task.description,
            status="pending",
            pet_id=task.pet_id,
        )
        if pet is not None:
            pet.add_task(new_task)
        new_event = Event(datetime=new_dt)
        self.schedule_task(new_task, new_event, schedule)
        return new_task

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
        for existing in event.tasks:
            if existing.pet_id is not None and existing.pet_id == task.pet_id:
                print(
                    f"[WARNING] Conflict at {event.datetime}: pet_id={task.pet_id} "
                    f"already has '{existing.name}'. Adding '{task.name}' anyway."
                )
                break
        event.add_task(task)
        if event not in schedule.events:
            schedule.add_event(event)

    def get_tasks_sorted_by_priority(self, owner: Owner) -> List[Task]:
        """Return all owner tasks ordered high > medium > low."""
        return sorted(self.get_tasks_by_owner(owner), key=lambda t: _PRIORITY_ORDER.get(t.priority, 99))

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by their earliest scheduled event time (HH:MM).
        Tasks with no scheduled event are placed at the end."""
        task_times: dict[int, str] = {}
        for schedule in self.schedules:
            for event in schedule.events:
                event_time = event.get_time()
                for task in event.tasks:
                    if id(task) not in task_times:
                        task_times[id(task)] = event_time
        return sorted(tasks, key=lambda t: tuple(map(int, task_times[id(t)].split(":")))
                                           if id(t) in task_times and task_times[id(t)]
                                           else (24, 0))


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    scheduler: Scheduler = field(default_factory=Scheduler)
    id: int = field(default_factory=_next_id)

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
