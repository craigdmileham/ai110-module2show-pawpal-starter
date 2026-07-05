# PawPal Pet Care App - UML Diagram

```mermaid
classDiagram
    class Owner {
        -name: String
        -id: int
        -pets: List~Pet~
        -schedule: Schedule
        +getName(): String
        +getPets(): List~Pet~
        +addPet(pet: Pet): void
        +removePet(pet: Pet): void
        +getSchedule(): Schedule
    }

    class Pet {
        -name: String
        -id: int
        -type: String
        -breed: String
        -tasks: List~Task~
        -medications: List~Medication~
        +getName(): String
        +getType(): String
        +getBreed(): String
        +getTasks(): List~Task~
        +addTask(task: Task): void
        +removeTask(task: Task): void
        +getMedications(): List~Medication~
        +addMedication(med: Medication): void
        +removeMedication(med: Medication): void
    }

    class Task {
        -name: String
        -id: int
        -type: String
        -duration: int
        -recurring: Boolean
        -priority: String
        -description: String
        -status: String
        +getName(): String
        +getType(): String
        +getDuration(): int
        +setDuration(): int
        +getPriority(): String
        +setPriority(): String
        +getDescription(): String
        +setDescription(): String
        +getStatus(): String
        +setStatus(status: String): void
    }

    class Medication {
        -name: String
        -id: int
        -dosage: String
        -frequency: String
        +getName(): String
        +getDosage(): String
        +getFrequency(): String
    }

    class Schedule {
        -id: int
        -events: List~Event~
        +addEvent(event: Event): void
        +removeEvent(event: Event): void
        +getEvents(): List~Event~
    }

    class Event {
        -id: int
        -datetime: DateTime
        -tasks: List~Task~
        +getDate(): Date
        +getTime(): Time
        +getTasks(): List~Task~
        +addTask(task: Task): void
        +removeTask(task: Task): void
    }

    class Scheduler {
        -id: int
        -schedules: List~Schedule~
        +getTasksByPet(pet: Pet): List~Task~
        +getTasksByOwner(owner: Owner): List~Task~
        +getTasksByStatus(status: String): List~Task~
        +getTasksByPriority(priority: String): List~Task~
        +getUpcomingTasks(owner: Owner): List~Task~
        +markTaskComplete(task: Task): void
        +reassignTask(task: Task, pet: Pet): void
        +addSchedule(schedule: Schedule): void
        +removeSchedule(schedule: Schedule): void
        +getSchedules(): List~Schedule~
        +scheduleTask(task: Task, event: Event, schedule: Schedule): void
    }

    Owner "1" --> "*" Pet
    Pet "1" --> "*" Task
    Pet "1" --> "*" Medication
    Owner "1" --> "1" Schedule
    Schedule "1" --> "*" Event
    Event "1" --> "*" Task
    Owner "1" --> "1" Scheduler
    Scheduler "1" --> "*" Schedule
```

## Relationships

- **Owner has Pets**: One owner can own multiple pets (1-to-many)
- **Pet has Tasks**: One pet can have multiple tasks (1-to-many)
- **Pet takes Medications**: One pet can take multiple medications (1-to-many)
- **Owner maintains Schedule**: One owner has one schedule (1-to-1)
- **Owner uses Scheduler**: One owner has one scheduler (1-to-1) that retrieves, organizes, and manages tasks across all pets
- **Scheduler manages Schedules**: One scheduler manages multiple schedules (1-to-many), adjusting and organizing them across all pets
