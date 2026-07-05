from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

_id_counter = itertools.count(1)


@dataclass
class Medication:
    name: str
    dosage: str
    frequency: str
    id: int = field(default_factory=lambda: next(_id_counter))

    def getName(self) -> str:
        return self.name

    def getDosage(self) -> str:
        return self.dosage

    def getFrequency(self) -> str:
        return self.frequency


@dataclass
class Task:
    name: str
    type: str
    duration: int  # minutes
    priority: str = "medium"
    description: str = ""
    recurring: bool = False
    frequency: str = "Once"  # "Once" | "Daily" | "Weekly"
    status: str = "pending"
    id: int = field(default_factory=lambda: next(_id_counter))

    def getName(self) -> str:
        return self.name

    def getType(self) -> str:
        return self.type

    def getDuration(self) -> int:
        return self.duration

    def setDuration(self, value: int) -> None:
        self.duration = value

    def getPriority(self) -> str:
        return self.priority

    def setPriority(self, value: str) -> None:
        self.priority = value

    def getDescription(self) -> str:
        return self.description

    def setDescription(self, value: str) -> None:
        self.description = value

    def getStatus(self) -> str:
        return self.status

    def setStatus(self, value: str) -> None:
        self.status = value


@dataclass
class Event:
    datetime: datetime
    tasks: List[Task] = field(default_factory=list)
    id: int = field(default_factory=lambda: next(_id_counter))

    @property
    def end_time(self) -> datetime:
        total = sum(t.duration for t in self.tasks)
        return self.datetime + timedelta(minutes=max(total, 1))

    def getDate(self):
        return self.datetime.date()

    def getTime(self):
        return self.datetime.time()

    def getTasks(self) -> List[Task]:
        return list(self.tasks)

    def addTask(self, task: Task) -> None:
        self.tasks.append(task)

    def removeTask(self, task: Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Schedule:
    events: List[Event] = field(default_factory=list)
    id: int = field(default_factory=lambda: next(_id_counter))

    def addEvent(self, event: Event) -> None:
        self.events.append(event)

    def removeEvent(self, event: Event) -> None:
        if event in self.events:
            self.events.remove(event)

    def getEvents(self) -> List[Event]:
        return list(self.events)


@dataclass
class Pet:
    name: str
    species: str  # stored as species to avoid shadowing Python builtin `type`
    breed: str = ""
    tasks: List[Task] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)
    id: int = field(default_factory=lambda: next(_id_counter))

    def getName(self) -> str:
        return self.name

    def getType(self) -> str:
        return self.species

    def getBreed(self) -> str:
        return self.breed

    def getTasks(self) -> List[Task]:
        return list(self.tasks)

    def addTask(self, task: Task) -> None:
        self.tasks.append(task)

    def removeTask(self, task: Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)

    def getMedications(self) -> List[Medication]:
        return list(self.medications)

    def addMedication(self, med: Medication) -> None:
        self.medications.append(med)

    def removeMedication(self, med: Medication) -> None:
        if med in self.medications:
            self.medications.remove(med)


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    schedule: Optional[Schedule] = None
    id: int = field(default_factory=lambda: next(_id_counter))

    def __post_init__(self):
        if self.schedule is None:
            self.schedule = Schedule()

    def getName(self) -> str:
        return self.name

    def getPets(self) -> List[Pet]:
        return list(self.pets)

    def addPet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def removePet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)

    def getSchedule(self) -> Schedule:
        return self.schedule
