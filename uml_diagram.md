# PawPal Pet Care App - UML Diagram

```mermaid
classDiagram
    class Owner {
        -name: String
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
        -type: String
        -duration: int
        -priority: String
        -description: String
        +getName(): String
        +getType(): String
        +getDuration(): int
        +getPriority(): String
        +getDescription(): String
    }

    class Medication {
        -name: String
        -dosage: String
        -frequency: String
        +getName(): String
        +getDosage(): String
        +getFrequency(): String
    }

    class Schedule {
        -events: List~Event~
        +addEvent(event: Event): void
        +removeEvent(event: Event): void
        +getEvents(): List~Event~
    }

    class Event {
        -date: Date
        -time: Time
        -tasks: List~Task~
        +getDate(): Date
        +getTime(): Time
        +getTasks(): List~Task~
        +addTask(task: Task): void
        +removeTask(task: Task): void
    }

    Owner "1" --> "*" Pet
    Pet "1" --> "*" Task
    Pet "1" --> "*" Medication
    Owner "1" --> "1" Schedule
    Schedule "1" --> "*" Event
    Event "1" --> "*" Task
```

## Relationships

- **Owner has Pets**: One owner can own multiple pets (1-to-many)
- **Pet has Tasks**: One pet can have multiple tasks (1-to-many)
- **Pet takes Medications**: One pet can take multiple medications (1-to-many)
- **Owner maintains Schedule**: One owner has one schedule (1-to-1)
