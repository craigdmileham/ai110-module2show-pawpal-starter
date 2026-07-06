import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Schedule, Event, Scheduler
from dummy_data import load_dummy_data

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session state init ---
if "owners" not in st.session_state:
    seed_owner, scheduler = load_dummy_data()
    st.session_state.owners = [seed_owner]
    st.session_state.scheduler = scheduler
    st.session_state.schedule = Schedule()
    scheduler.add_schedule(st.session_state.schedule)

scheduler: Scheduler = st.session_state.scheduler
schedule: Schedule = st.session_state.schedule

# --- Owners ---
st.subheader("Owners")

owner_names = [o.get_name() for o in st.session_state.owners]
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    selected_owner_name = st.selectbox("Active owner", owner_names)
with col2:
    new_owner_name = st.text_input("Add new owner", placeholder="Owner name", key="new_owner_name")
with col3:
    st.write("")
    st.write("")  # nudge button down to align with inputs
    if st.button("Add", use_container_width=True):
        if new_owner_name.strip():
            if new_owner_name.strip() in owner_names:
                st.warning(f"Owner '{new_owner_name.strip()}' already exists.")
            else:
                st.session_state.owners.append(Owner(name=new_owner_name.strip()))
                st.rerun()

owner: Owner = next(o for o in st.session_state.owners if o.get_name() == selected_owner_name)

st.dataframe(
    [
        {"Owner": o.get_name(), "Pets": len(o.get_pets()), "Tasks": sum(len(p.get_tasks()) for p in o.get_pets())}
        for o in st.session_state.owners
    ],
    use_container_width=True,
)

st.divider()

# --- Pets ---
st.subheader(f"Pets — {owner.get_name()}")

with st.expander("Add a new pet"):
    new_pet_name = st.text_input("New pet name", key="new_pet_name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    new_pet_breed = st.text_input("Breed (optional)", key="new_pet_breed")
    if st.button("Add pet"):
        if new_pet_name.strip():
            new_pet = Pet(name=new_pet_name.strip(), species=new_pet_species, breed=new_pet_breed.strip() or None)
            owner.add_pet(new_pet)
            st.success(f"Added {new_pet_name} to {owner.get_name()}!")
            st.rerun()

pet_rows = [
    {
        "Pet": p.get_name(),
        "Species": p.get_species(),
        "Breed": p.get_breed() or "—",
        "Tasks": len(p.get_tasks()),
    }
    for p in owner.get_pets()
]
st.dataframe(pet_rows, use_container_width=True)

# --- Medications ---
st.markdown("#### Medications")

med_rows = [
    {
        "Pet": p.get_name(),
        "Medication": m.get_name(),
        "Dosage": m.get_dosage(),
        "Frequency": m.get_frequency(),
    }
    for p in owner.get_pets()
    for m in p.get_medications()
]
if med_rows:
    st.dataframe(med_rows, use_container_width=True)
else:
    st.caption("No medications recorded.")

with st.expander("Add / remove a medication"):
    med_pet_options = [p.get_name() for p in owner.get_pets()]
    if med_pet_options:
        med_pet_name = st.selectbox("Pet", med_pet_options, key="med_pet")
        med_pet = next(p for p in owner.get_pets() if p.get_name() == med_pet_name)

        st.markdown("**Add medication**")
        col1, col2, col3 = st.columns(3)
        with col1:
            med_name = st.text_input("Name", placeholder="e.g. Apoquel", key="med_name")
        with col2:
            med_dosage = st.text_input("Dosage", placeholder="e.g. 5.4mg", key="med_dosage")
        with col3:
            med_freq = st.text_input("Frequency", placeholder="e.g. once daily", key="med_freq")
        if st.button("Add medication"):
            if med_name.strip():
                from pawpal_system import Medication
                med_pet.add_medication(Medication(name=med_name.strip(), dosage=med_dosage.strip(), frequency=med_freq.strip()))
                st.success(f"Added {med_name} for {med_pet.get_name()}.")
                st.rerun()
            else:
                st.error("Medication name is required.")

        st.markdown("**Remove medication**")
        remove_options = {f"{m.get_name()} ({m.get_dosage()})": m for m in med_pet.get_medications()}
        if remove_options:
            remove_label = st.selectbox("Select medication to remove", list(remove_options.keys()), key="med_remove")
            if st.button("Remove medication"):
                med_pet.remove_medication(remove_options[remove_label])
                st.success(f"Removed {remove_label} from {med_pet.get_name()}.")
                st.rerun()
        else:
            st.caption(f"{med_pet.get_name()} has no medications to remove.")
    else:
        st.info("Add a pet above before managing medications.")

st.divider()

# --- Tasks ---
st.subheader("Tasks")

pending_count = len(scheduler.get_tasks_by_status(owner, "pending"))
complete_count = len(scheduler.get_tasks_by_status(owner, "complete"))
m1, m2 = st.columns(2)
m1.metric("Pending", pending_count)
m2.metric("Complete", complete_count)

with st.expander("Add a task"):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    task_type = st.selectbox("Task type", ["exercise", "feeding", "grooming", "medication", "other"])
    description = st.text_input("Description (optional)", value="")
    recurring = st.checkbox("Recurring?")
    frequency = None
    if recurring:
        frequency = st.selectbox("Frequency", ["daily", "weekly"])

    assign_options = [p.get_name() for p in owner.get_pets()]
    if assign_options:
        assign_to = st.selectbox("Assign to pet", assign_options, key="assign_pet")
        target_pet = next((p for p in owner.get_pets() if p.get_name() == assign_to), None)
    else:
        st.info("Add a pet above before adding tasks.")
        target_pet = None

    if st.button("Add task"):
        if target_pet is None:
            st.error("Select a pet first.")
        else:
            task = Task(
                name=task_title,
                type=task_type,
                duration=int(duration),
                recurring=recurring,
                frequency=frequency,
                priority=priority,
                description=description,
                status="pending",
            )
            target_pet.add_task(task)
            st.success(f"Task '{task_title}' added to {target_pet.get_name()}.")
            st.rerun()

all_tasks = [
    (p, t)
    for p in owner.get_pets()
    for t in p.get_tasks()
]

if all_tasks:
    task_rows = [
        {
            "Pet": p.get_name(),
            "Task": t.get_name(),
            "Type": t.get_type(),
            "Duration (min)": t.get_duration(),
            "Priority": t.get_priority(),
            "Recurring": "Yes" if t.recurring else "No",
            "Status": t.get_status(),
        }
        for p, t in all_tasks
    ]
    st.dataframe(task_rows, use_container_width=True)
else:
    st.info("No tasks yet. Add one above.")

st.markdown("#### Mark Task Complete")

pet_map = {p.id: p.get_name() for o in st.session_state.owners for p in o.get_pets()}
pending_tasks = [t for p in owner.get_pets() for t in p.get_tasks() if t.get_status() == "pending"]
if pending_tasks:
    task_options = {
        f"{pet_map.get(t.pet_id, '?')} — {t.get_name()}": t
        for t in pending_tasks
    }
    selected_label = st.selectbox("Select task to complete", list(task_options.keys()), key="complete_select")
    task_to_complete = task_options[selected_label]

    if st.button("Mark complete"):
        pet_for_task = next(
            (p for o in st.session_state.owners for p in o.get_pets() if p.id == task_to_complete.pet_id),
            None,
        )
        new_task = scheduler.mark_task_complete(
            task_to_complete,
            schedule=schedule,
            pet=pet_for_task,
        )
        if new_task:
            st.success(f"'{task_to_complete.get_name()}' marked complete. Next occurrence scheduled!")
        else:
            st.success(f"'{task_to_complete.get_name()}' marked complete.")
        st.rerun()
else:
    st.info("No pending tasks to complete.")

st.divider()

# --- Build Schedule ---
st.subheader("Build Schedule")

selected_owner_names = st.multiselect(
    "Include owners in schedule",
    options=[o.get_name() for o in st.session_state.owners],
    default=[owner.get_name()],
)
selected_owners = [o for o in st.session_state.owners if o.get_name() in selected_owner_names]
all_pets_in_schedule = [p for o in selected_owners for p in o.get_pets()]
all_schedule_tasks = [(p, t) for p in all_pets_in_schedule for t in p.get_tasks()]

if all_schedule_tasks:
    start_time = st.time_input(
        "Schedule start time",
        value=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0).time(),
    )
    gap_minutes = st.number_input("Gap between tasks (minutes)", min_value=0, max_value=60, value=5)

    if st.button("Generate schedule"):
        base_dt = datetime.combine(datetime.today(), start_time)
        offset = 0
        scheduled = []
        conflicts = []

        for pet, task in all_schedule_tasks:
            event_dt = base_dt + timedelta(minutes=offset)
            event = Event(datetime=event_dt.isoformat())
            warning = scheduler.schedule_task(task, event, schedule, pets=all_pets_in_schedule)
            scheduled.append((pet, task, event_dt))
            offset += task.get_duration() + gap_minutes
            if warning:
                conflicts.append(warning)

        owner_labels = ", ".join(o.get_name() for o in selected_owners)
        st.success(f"Scheduled {len(scheduled)} task(s) for {owner_labels}!")

        schedule_rows = []
        for pet, task, dt in scheduled:
            end_dt = dt + timedelta(minutes=task.get_duration())
            schedule_rows.append({
                "Start": dt.strftime("%I:%M %p"),
                "End": end_dt.strftime("%I:%M %p"),
                "Owner": next(o.get_name() for o in selected_owners if pet in o.get_pets()),
                "Pet": pet.get_name(),
                "Task": task.get_name(),
                "Duration (min)": task.get_duration(),
                "Priority": task.get_priority(),
                "Type": task.get_type(),
            })
        st.dataframe(schedule_rows, use_container_width=True)

        if conflicts:
            st.markdown("**Conflicts detected:**")
            for msg in conflicts:
                st.warning(msg)
elif selected_owner_names:
    st.info("No tasks found for the selected owners. Add tasks above before building a schedule.")
else:
    st.info("Select at least one owner above to build a schedule.")

st.divider()

# --- Task Dashboard ---
st.subheader("Task Dashboard")

window = st.slider("Look-ahead window (days)", min_value=1, max_value=30, value=7)
upcoming = scheduler.get_upcoming_tasks(owner, window=window)
st.metric("Upcoming tasks (within window)", len(upcoming))

st.markdown("#### All Tasks — Sorted by Priority")
st.caption("High → Medium → Low, then by scheduled time within each priority.")

sorted_tasks = scheduler.get_tasks_sorted_by_priority(owner)
pet_map = {p.id: p.get_name() for o in st.session_state.owners for p in o.get_pets()}

if sorted_tasks:
    dashboard_rows = [
        {
            "Pet": pet_map.get(t.pet_id, "—"),
            "Task": t.get_name(),
            "Priority": t.get_priority(),
            "Type": t.get_type(),
            "Duration (min)": t.get_duration(),
            "Recurring": "Yes" if t.recurring else "No",
            "Frequency": t.frequency if t.frequency else "—",
            "Status": t.get_status(),
        }
        for t in sorted_tasks
    ]
    st.dataframe(dashboard_rows, use_container_width=True)
else:
    st.info("No tasks found.")

st.divider()

# --- Tasks by Time ---
st.subheader("Tasks by Time")
st.caption("All tasks for the active owner sorted by their scheduled start time. Unscheduled tasks appear last.")

all_owner_tasks_flat = [t for p in owner.get_pets() for t in p.get_tasks()]
time_sorted_tasks = scheduler.sort_by_time(all_owner_tasks_flat)

if time_sorted_tasks:
    time_rows = [
        {
            "Pet": pet_map.get(t.pet_id, "—"),
            "Task": t.get_name(),
            "Type": t.get_type(),
            "Duration (min)": t.get_duration(),
            "Priority": t.get_priority(),
            "Status": t.get_status(),
        }
        for t in time_sorted_tasks
    ]
    st.dataframe(time_rows, use_container_width=True)
else:
    st.info("No tasks found. Add tasks above.")

