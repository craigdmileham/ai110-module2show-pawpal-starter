import streamlit as st
from datetime import datetime, timedelta

from models import Event, Pet, Task
from scheduler import Scheduler, ScheduleConflictError
from dummy_data import load_dummy_data

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner, st.session_state.scheduler = load_dummy_data()

owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# --- Owner + Pet Setup ---
st.subheader("Owner & Pet")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=owner.getName())
    owner.name = owner_name

with col2:
    pet_names = [p.getName() for p in owner.getPets()]
    selected_pet_name = st.selectbox("Active pet", pet_names if pet_names else ["(none)"])

active_pet = next((p for p in owner.getPets() if p.getName() == selected_pet_name), None)

with st.expander("Add a new pet"):
    new_pet_name = st.text_input("New pet name", key="new_pet_name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    new_pet_breed = st.text_input("Breed (optional)", key="new_pet_breed")
    if st.button("Add pet"):
        if new_pet_name.strip():
            new_pet = Pet(name=new_pet_name.strip(), species=new_pet_species, breed=new_pet_breed.strip())
            owner.addPet(new_pet)
            st.success(f"Added {new_pet_name}!")
            st.rerun()

st.divider()

# --- Task Management ---
st.subheader("Tasks")

if active_pet:
    st.caption(f"Managing tasks for **{active_pet.getName()}** ({active_pet.getType()})")

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        task_type = st.text_input("Task type", value="exercise")
    with col5:
        recurring = st.checkbox("Recurring?")
    frequency = "Once"
    if recurring:
        frequency = st.selectbox("Frequency", ["Daily", "Weekly"])

    if st.button("Add task"):
        if task_title.strip():
            task = Task(
                name=task_title.strip(),
                type=task_type.strip() or "general",
                duration=int(duration),
                priority=priority,
                recurring=recurring,
                frequency=frequency,
            )
            active_pet.addTask(task)
            st.success(f"Added task: {task_title}")

    tasks = active_pet.getTasks()
    if tasks:
        st.write(f"Tasks for {active_pet.getName()}:")
        rows = [
            {
                "Title": t.getName(),
                "Type": t.getType(),
                "Duration (min)": t.getDuration(),
                "Priority": t.getPriority(),
                "Recurring": "Yes" if t.recurring else "No",
                "Frequency": t.frequency if t.recurring else "—",
                "Status": t.getStatus(),
            }
            for t in tasks
        ]
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("No pets found. Add a pet above.")

st.divider()

# --- Schedule Builder ---
st.subheader("Build Schedule")

if active_pet:
    start_time = st.time_input("Schedule start time", value=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0).time())
    gap_minutes = st.number_input("Gap between tasks (minutes)", min_value=0, max_value=60, value=5)

    if st.button("Generate schedule"):
        tasks = active_pet.getTasks()
        if not tasks:
            st.warning("No tasks to schedule. Add tasks above first.")
        else:
            base_dt = datetime.combine(datetime.today(), start_time)
            offset = 0
            conflicts = []
            scheduled = []

            for task in tasks:
                event_dt = base_dt + timedelta(minutes=offset)
                event = Event(datetime=event_dt)
                try:
                    scheduler.scheduleTask(task, event, owner.getSchedule())
                    scheduled.append((task, event_dt))
                    offset += task.getDuration() + gap_minutes
                except ScheduleConflictError as e:
                    conflicts.append(str(e))

            if scheduled:
                st.success(f"Scheduled {len(scheduled)} task(s)!")
                st.markdown("### Schedule")
                for task, dt in scheduled:
                    end_dt = dt + timedelta(minutes=task.getDuration())
                    st.markdown(
                        f"- **{dt.strftime('%I:%M %p')} – {end_dt.strftime('%I:%M %p')}** "
                        f"| {task.getName()} ({task.getDuration()} min)"
                    )

            if conflicts:
                st.markdown("### Conflicts detected")
                for msg in conflicts:
                    st.warning(msg)

st.divider()

# --- Upcoming Tasks ---
st.subheader("Upcoming Tasks")

upcoming = scheduler.getUpcomingTasks(owner)
if upcoming:
    st.markdown("### Why this order?")
    st.caption("Sorted by priority (high → low), then shortest duration first.")
    rows = [
        {
            "Task": t.getName(),
            "Priority": t.getPriority(),
            "Duration (min)": t.getDuration(),
            "Recurring": "Yes" if t.recurring else "No",
            "Frequency": t.frequency if t.recurring else "—",
            "Status": t.getStatus(),
        }
        for t in upcoming
    ]
    st.dataframe(rows, use_container_width=True)

    # Mark complete
    task_names = [t.getName() for t in upcoming]
    complete_task_name = st.selectbox("Mark task complete", ["(select)"] + task_names, key="complete_select")
    if st.button("Mark complete"):
        task_to_complete = next((t for t in upcoming if t.getName() == complete_task_name), None)
        if task_to_complete:
            scheduler.markTaskComplete(task_to_complete)
            st.success(f"Marked '{complete_task_name}' as complete.")
            st.rerun()
else:
    st.info("No upcoming tasks scheduled yet. Use 'Build Schedule' above.")
