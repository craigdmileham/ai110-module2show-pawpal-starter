# PawPal+ Project Reflection

## 1. System Design

Core Actions
- Setup owner and their schedules
- Add/View pets and their related tasks
- Viewing a organized daily task view
- Schedule each pet task adhering closest to each owner's schedule

Objects:

- Owner
    * Name
    * List of Pets
    * Schedule
- Pets
    * Name
    * Type of Pet
    * Breed
    * List of Tasks
    * Medications
- Tasks
    * Name
    * Type (walk, feeding, etc.)
    * Duration
    * Priority
    * Description
- Scheduler
    * Name
    * Get Schedules
    * Schedule Event
    * Delete Event
- Events
    * Name
    * Tasks
    * DateTime
- Medication
    * Name
    * Dosage
    * Frequency


**a. Initial design**

- Briefly describe your initial UML design.
  The initial design tries to keep in mind that Owners and their Pets each have individual schedules. It also respects that tasks and events are not exactly the same thing so tasks can exist on their own without being tied to a given scheduled event.

- What classes did you include, and what responsibilities did you assign to each?

  The initial design defines the Owner, Pet, Medication, Task, Event, Schedule, and Scheduler classes. The Owner keeps track of their Schedule and Pets. Pets keep track of their related tasks and medications. Medications keep only have basic properties. Tasks keep track of their duration, status, priority, and whether they are recurring. Events exist with or without tasks and can have tasks be associated with them. Schedules keep track of events associated with them. Finally the Scheduler finds and arranges tasks to the corresponding schedules of pets and owners.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

My design changed after Claude looked over the skeleton of the implementation and found several missing relationships and potential logic flaws. One of the key changes needed was ownership of Schedules. In my first implementation the Owner also held ownership of Schedules so that changed to just the Scheduler owning the Schedules and changing each of the access methods to include the Owner as a parameter. I agreed that this needed to be changed in order to ensure that ownership was clear and that it would make it simpler to implement multiuser features later on.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

    My scheduler considers time and priority of tasks. I decided to focus on these because a pet owner should be focusing on the needs of their pet as opposed to their own preferences. Priority trumps time in this way but only when tasks occur at the same time. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

    My scheduler doesn't take into account the duration of a task when addressing task conflicts of different priority. Expanding on that tradeoff, you'd want to have a task with a higher priority to rise to the top over a lower priority task given time constraints. It is reasonable here because balancing the duration of a task with the owner's ability to perform it requires a certain amount of buffer time. In reality a reasonable expectation is to schedule based on 15 minute chunks to accomodate for variance. That would add a good amount of complexity to the scheduling algorithm.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

    I used AI for brainstorming, refactoring, and task planning. I found that the most useful prompts in this process were to ask for explanations of a given functionality and then to follow up with implementation steps. I also found that mentioning a specific functionality of Python or Streamlit would yield better results for implementation. I also found that using Claude Code's planning mode led me to feel more confident about letting it go ahead and make changes automatically as it was following along with the plan. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I didn't catch it at first and had to go back to correct it but during the class implementation all of the constructors would require specifying the object's ID. That is obviously bad practice that I went back and fixed later. While refining the task scheduling algorithm, the initial pass led the suggestion to forgetting a multi-pet scenario so I had to refine and prompt a couple of more times before getting a usable result.

I manually tested the UI implementation but I found myself adding in the testing file as context to each of my prompts and having Claude go through and test after each implementation. I'd go back and confirm that the tests were not just returning some false value and were actually testing functionality appropriately.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the CRUD behaviors related to adding owners, pets, tasks, and the schedule. These tests were important to ensuring that the app was going to function properly after a lot of iteration over the functionality and implementation. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm pretty confident that the scheduler works really well. I tested each core part of it's functionality prior to continuing implementation of the UI and once I did, Claude had gone ahead and just come up with an additional feature allowing the user to add an offset to the task timings while generating schedules. That feature works pretty flawlessly. 

The edge cases I'd want to test more are with input validation. I'd also want to make sure that references to owners and pets were being done by their IDs instead of other values to ensure that actions acted on the expected owner/pet every single time.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with my initial design. I was able to work with Claude to really refine the rough edges off and I think it actually works well.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd go back and expand on the user interface. My system design kept in mind that owner's schedules and pet's schedules differ so there is the opportunity to refine that idea in a second iteration. I'd like to expand with the idea that there can be co-ownership of pet and you may want to split tasks between owners depending on their schedules.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that AI can be steered in a clearer direction if you have some idea of how you want to implement a feature using a specific algorithm, data structures, language feature, etc. I also learned that doing that while using a planning task and extra added file context can really speed up implementation without as many brittle results.