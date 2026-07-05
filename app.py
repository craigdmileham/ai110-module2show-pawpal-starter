import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule, Event, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# owners: dict of owner_name -> Owner
if "owners" not in st.session_state:
    st.session_state.owners = {}

st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add owner & pet"):
    owners = st.session_state.owners
    if owner_name not in owners:
        owners[owner_name] = Owner(name=owner_name)
    owner = owners[owner_name]

    existing_pet = next((p for p in owner.get_pets() if p.get_name() == pet_name), None)
    if existing_pet:
        st.info(f"{pet_name} already exists under {owner_name}.")
    else:
        pet = Pet(name=pet_name, species=species)
        owner.add_pet(pet)
        st.success(f"Added {pet_name} ({species}) under owner {owner_name}.")

if st.session_state.owners:
    st.write("Registered owners & pets:")
    st.table([
        {"Owner": o.get_name(), "Pet": p.get_name(), "Species": p.get_species()}
        for o in st.session_state.owners.values()
        for p in o.get_pets()
    ])

st.divider()
st.markdown("### Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

task_type = st.selectbox("Task type", ["exercise", "feeding", "grooming", "medication", "other"])
description = st.text_input("Description (optional)", value="")

all_pets = [
    (o, p)
    for o in st.session_state.owners.values()
    for p in o.get_pets()
]
pet_options = [f"{o.get_name()} → {p.get_name()}" for o, p in all_pets]

if pet_options:
    selected = st.selectbox("Assign task to", pet_options)
    selected_owner, selected_pet = all_pets[pet_options.index(selected)]
else:
    st.info("Add an owner & pet above before adding tasks.")
    selected_owner, selected_pet = None, None

if st.button("Add task"):
    if selected_pet is None:
        st.error("Add an owner & pet first.")
    else:
        task = Task(
            name=task_title,
            type=task_type,
            duration=int(duration),
            recurring=False,
            priority=priority,
            description=description,
            status="pending",
        )
        selected_pet.add_task(task)
        st.success(f"Task '{task_title}' added to {selected_pet.get_name()}.")

all_tasks = [
    (o, p, t)
    for o in st.session_state.owners.values()
    for p in o.get_pets()
    for t in p.get_tasks()
]

if all_tasks:
    st.write("Current tasks:")
    st.table([
        {
            "Owner": o.get_name(),
            "Pet": p.get_name(),
            "Name": t.get_name(),
            "Type": t.get_type(),
            "Duration (min)": t.get_duration(),
            "Priority": t.get_priority(),
            "Status": t.get_status(),
        }
        for o, p, t in all_tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
