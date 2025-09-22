import streamlit as st

from util.utils import get_tasks, save_task, Task, TaskStatus

if "tasks" not in st.session_state:
    st.session_state["tasks"] = get_tasks()

def add_task(title: str, description: str):
    new_id = len(st.session_state["tasks"]) + 1
    task = Task(
        id=new_id,
        title=title,
        description=description,
    )
    
    st.session_state.tasks.append(task.model_dump())
    save_task(st.session_state.tasks)

def update_task_status(task_id: int, new_status: TaskStatus):
    """Actualiza el estado de una tarea y vuelve a guardar el archivo."""
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["status"] = new_status.value
            save_task(st.session_state.tasks)
            st.rerun()
            break

def show_add_form():
    with st.expander("Agregar tarea", expanded=True):
        title = st.text_input("Título")
        description = st.text_area("Descripción")
        
        if st.button("Agregar"):
            if title and description:
                add_task(title, description)
                st.success("Tarea añadida con éxito!")
                st.rerun()
            else:
                st.warning("Por favor, ingresa un título y una descripción.")

def show_tasks_by_status(status: TaskStatus):
    tasks_to_display = [task for task in st.session_state.tasks if task["status"] == status.value]
    
    for task_data in tasks_to_display:
        with st.expander(f"**{task_data['title']}**"):
            st.markdown(f"_{task_data['description']}_")
            st.write(f"ID: {task_data['id']}")
            st.write(f"Creada: {task_data['timestamp']}")
            
            # Botones para cambiar el estado
            col1, col2 = st.columns(2)
            
            with col1:
                if status == TaskStatus.PENDING:
                    if st.button("▶️ En Progreso", key=f"to_progress_{task_data['id']}"):
                        update_task_status(task_data['id'], TaskStatus.IN_PROGRESS)
                if status == TaskStatus.COMPLETED:
                     if st.button("◀️ En Progreso", key=f"to_progress_from_completed_{task_data['id']}"):
                        update_task_status(task_data['id'], TaskStatus.IN_PROGRESS)
            
            with col2:
                if status != TaskStatus.COMPLETED:
                    if st.button("✅ Completar", key=f"to_completed_{task_data['id']}"):
                        update_task_status(task_data['id'], TaskStatus.COMPLETED)
                if status == TaskStatus.IN_PROGRESS:
                    if st.button("❌ Pendiente", key=f"to_pending_{task_data['id']}"):
                        update_task_status(task_data['id'], TaskStatus.PENDING)

def show_tasks():
    st.subheader("Tareas")
    col_pending, col_in_progress, col_completed = st.columns(3)

    with col_pending:
        st.markdown("<h3 style='text-align: center;'>⚠️Pendientes</h3>", unsafe_allow_html=True)
        show_tasks_by_status(TaskStatus.PENDING)

    with col_in_progress:
        st.markdown("<h3 style='text-align: center;'>📌En Progreso</h3>", unsafe_allow_html=True)
        show_tasks_by_status(TaskStatus.IN_PROGRESS)

    with col_completed:
        st.markdown("<h3 style='text-align: center;'>✅Completadas</h3>", unsafe_allow_html=True)
        show_tasks_by_status(TaskStatus.COMPLETED)

def main():
    st.header("To-Do App")
    show_add_form()
    show_tasks()

if __name__ == "__main__":
    main()