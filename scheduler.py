from __future__ import annotations

import itertools
from datetime import datetime, timedelta
from typing import List

from models import Event, Owner, Pet, Schedule, Task

_id_counter = itertools.count(1000)


class ScheduleConflictError(Exception):
    """Raised when scheduleTask detects a time overlap between events."""
    pass


class Scheduler:
    def __init__(self):
        self.id: int = next(_id_counter)
        self.schedules: List[Schedule] = []

    # --- Schedule management ---

    def addSchedule(self, schedule: Schedule) -> None:
        self.schedules.append(schedule)

    def removeSchedule(self, schedule: Schedule) -> None:
        if schedule in self.schedules:
            self.schedules.remove(schedule)

    def getSchedules(self) -> List[Schedule]:
        return list(self.schedules)

    # --- Query methods ---

    def getTasksByPet(self, pet: Pet) -> List[Task]:
        pet_task_ids = {t.id for t in pet.getTasks()}
        result = []
        for schedule in self.schedules:
            for event in schedule.getEvents():
                for task in event.getTasks():
                    if task.id in pet_task_ids:
                        result.append(task)
        return result

    def getTasksByOwner(self, owner: Owner) -> List[Task]:
        all_task_ids = {t.id for pet in owner.getPets() for t in pet.getTasks()}
        result = []
        for schedule in self.schedules:
            for event in schedule.getEvents():
                for task in event.getTasks():
                    if task.id in all_task_ids:
                        result.append(task)
        return result

    def getTasksByStatus(self, status: str) -> List[Task]:
        result = []
        for schedule in self.schedules:
            for event in schedule.getEvents():
                for task in event.getTasks():
                    if task.getStatus() == status:
                        result.append(task)
        return result

    def getTasksByPriority(self, priority: str) -> List[Task]:
        result = []
        for schedule in self.schedules:
            for event in schedule.getEvents():
                for task in event.getTasks():
                    if task.getPriority() == priority:
                        result.append(task)
        return result

    def getUpcomingTasks(self, owner: Owner) -> List[Task]:
        now = datetime.now()
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        result = []
        for event in owner.getSchedule().getEvents():
            if event.datetime >= now:
                for task in event.getTasks():
                    if task.getStatus() != "complete":
                        result.append(task)
        result.sort(key=lambda t: (priority_rank.get(t.getPriority(), 1), t.getDuration()))
        return result

    # --- Mutation methods ---

    def markTaskComplete(self, task: Task) -> None:
        task.setStatus("complete")

    def reassignTask(self, task: Task, pet: Pet) -> None:
        for schedule in self.schedules:
            for event in schedule.getEvents():
                for t in event.getTasks():
                    if t.id == task.id:
                        # find old pet and remove
                        pass  # pet-task link is on Pet, not Event; update below
        # Remove from any pet that currently owns it
        # (we don't have a direct back-reference, so we search all schedules' owners)
        # In practice, callers should also call old_pet.removeTask(task)
        pet.addTask(task)

    def scheduleTask(self, task: Task, event: Event, schedule: Schedule) -> None:
        event.addTask(task)
        if self._check_conflicts(event, schedule):
            event.removeTask(task)
            raise ScheduleConflictError(
                f"Task '{task.name}' at {event.datetime.strftime('%Y-%m-%d %H:%M')} "
                f"conflicts with an existing event."
            )
        if event not in schedule.getEvents():
            schedule.addEvent(event)
        if task.recurring:
            self._generate_recurring_events(task, event, schedule)

    # --- Internal helpers ---

    def _check_conflicts(self, new_event: Event, schedule: Schedule) -> bool:
        new_start = new_event.datetime
        new_end = new_event.end_time
        for event in schedule.getEvents():
            if event.id == new_event.id:
                continue
            if new_start < event.end_time and event.datetime < new_end:
                return True
        return False

    def _generate_recurring_events(
        self, task: Task, base_event: Event, schedule: Schedule, count: int = 7
    ) -> None:
        if task.frequency == "Daily":
            delta = timedelta(days=1)
        elif task.frequency == "Weekly":
            delta = timedelta(weeks=1)
        else:
            return  # "Once" — nothing to generate

        for i in range(1, count + 1):
            new_dt = base_event.datetime + delta * i
            new_task = Task(
                name=task.name,
                type=task.type,
                duration=task.duration,
                priority=task.priority,
                description=task.description,
                recurring=True,
                frequency=task.frequency,
            )
            new_event = Event(datetime=new_dt)
            try:
                # add directly to avoid infinite recursion — recurring tasks don't re-generate
                new_event.addTask(new_task)
                if not self._check_conflicts(new_event, schedule):
                    schedule.addEvent(new_event)
            except Exception:
                pass  # skip conflicting future instances silently
