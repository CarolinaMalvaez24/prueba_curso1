import streamlit as st
from datetime import datetime

# Utilidades
from util.util import (
    get_tasks, save_tasks, Task, TaskStatus,
    update_task, delete_task
)

# -----------------------------
# Estado inicial
# -----------------------------
if "tasks" not in st.session_state:
    st.session_state["tasks"] = get_tasks() or []

if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = {}  # { task_id: bool }

# -----------------------------
# Helpers
# -----------------------------
def _date_of(ts: str) -> str:
    """YYYY-MM-DD o fecha actual si no hay timestamp."""
    return ts[:10] if ts else datetime.now().strftime("%Y-%m-%d")

def _get_task_from_state(task_id: int) -> dict | None:
    for t in st.session_state["tasks"]:
        if int(t.get("id")) == int(task_id):
            return t
    return None

def add_task(title: str, description: str):
    """Crear y persistir nueva tarea."""
    title, description = (title or "").strip(), (description or "").strip()
    if not title:
        st.warning("El título es obligatorio.", icon="⚠️")
        return
    next_id = (max([t.get("id", 0) for t in st.session_state["tasks"]], default=0) + 1)
    task = Task(id=next_id, title=title, description=description)
    st.session_state["tasks"].append(task.model_dump())
    save_tasks(st.session_state["tasks"])
    st.success("Tarea agregada.", icon="✅")
    st.rerun()

def _update_task_status(task_id: int, new_status: TaskStatus):
    update_task(task_id, status=new_status)
    st.session_state["tasks"] = get_tasks()
    st.rerun()

def _update_task_fields(task_id: int, title: str, description: str):
    update_task(task_id, title=title.strip(), description=description.strip())
    st.session_state["tasks"] = get_tasks()
    st.rerun()

def _delete_task_by_id(task_id: int):
    if delete_task(task_id):
        st.session_state["tasks"] = get_tasks()
        st.success("Tarea eliminada.", icon="🗑️")
        st.rerun()
    else:
        st.error("No se pudo eliminar la tarea.", icon="❌")

# -----------------------------
# Diálogo de edición
# -----------------------------
@st.dialog("Edit Task")
def edit_task_dialog(task_id: int):
    """Modal para editar o eliminar una tarea."""
    task = _get_task_from_state(task_id)
    if not task:
        st.error("No se encontró la tarea.", icon="❌")
        if st.button("Cerrar"):
            st.rerun()
        return

    # Inputs con valores actuales
    title = st.text_input("Título", value=task.get("title", ""), key=f"title_{task_id}")
    description = st.text_area("Descripción", value=task.get("description", ""), key=f"desc_{task_id}", height=140)

    col_save, col_delete = st.columns(2)

    # Guardar cambios
    with col_save:
        if st.button("Guardar cambios", type="primary", key=f"save_{task_id}", use_container_width=True):
            if not title.strip():
                st.warning("El título no puede estar vacío.", icon="⚠️")
            else:
                _update_task_fields(task_id, title, description)

    # Eliminar con botón rojo + ícono de basura
    with col_delete:
        # CSS para botón primario rojo
        st.markdown(
            """
            <style>
            div[data-testid="stButton"] button[kind="primary"].delete-btn {
                background-color: #e74c3c;
                color: white;
            }
            div[data-testid="stButton"] button[kind="primary"].delete-btn:hover {
                background-color: #c0392b;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("🗑️ Delete", key=f"del_in_modal_{task_id}",
                     type="primary", use_container_width=True,
                     help="Eliminar esta tarea", args=(), kwargs={},
                     ):
            _delete_task_by_id(task_id)

    st.caption("Tip: también puedes borrar o marcar como hecha desde la tarjeta.")

# -----------------------------
# UI: Crear
# -----------------------------
def show_add_form():
    with st.expander("Agregar tarea", expanded=True):
        title = st.text_input("Título")
        description = st.text_area("Descripción", height=140)
        if st.button("Agregar"):
            add_task(title, description)

# -----------------------------
# UI: Listado por estado
# -----------------------------
def show_tasks_by_status(status: TaskStatus):
    """Columna por estado con botones Done / Edit / Delete por tarea."""
    tasks = [t for t in st.session_state["tasks"]
             if (t.get("status") or TaskStatus.PENDING.value) == status.value]

    # Encabezado de columna
    if status is TaskStatus.PENDING:
        st.warning("Pending", icon="⚠️")
    elif status is TaskStatus.IN_PROGRESS:
        st.info("In progress", icon="📌")
    else:
        st.success("Completed", icon="✅")

    tasks_sorted = sorted(tasks,
                          key=lambda x: (x.get("timestamp", ""), x.get("id", 0)),
                          reverse=True)

    for task in tasks_sorted:
        task_id = task["id"]
        title = task.get("title", "(sin título)")
        desc = task.get("description", "")
        ts = _date_of(task.get("timestamp", ""))
        current_status = task.get("status") or TaskStatus.PENDING.value

        with st.expander(title, expanded=False):
            st.markdown(f":green[{ts}]")
            st.write(desc if desc.strip() else "Sin descripción")

            # ---- Botones principales ----
            col_done, col_edit, col_del = st.columns(3)

            # DONE en Pending / In Progress
            if current_status in (TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value):
                with col_done:
                    if st.button("Done", key=f"done_{task_id}", use_container_width=True):
                        _update_task_status(task_id, TaskStatus.COMPLETED)
            else:
                with col_done:
                    st.caption("")

            # EDIT abre modal
            with col_edit:
                if st.button("Edit", key=f"edit_{task_id}", use_container_width=True):
                    edit_task_dialog(task_id)

            # DELETE con confirmación inline
            with col_del:
                if st.button("Delete", key=f"delete_{task_id}", use_container_width=True):
                    st.session_state["confirm_delete"][task_id] = True

            if st.session_state["confirm_delete"].get(task_id):
                st.warning("¿Eliminar esta tarea?", icon="🗑️")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Sí, eliminar", key=f"yesdel_{task_id}", use_container_width=True):
                        _delete_task_by_id(task_id)
                with c2:
                    if st.button("Cancelar", key=f"nodel_{task_id}", use_container_width=True):
                        st.session_state["confirm_delete"][task_id] = False

def show_tasks():
    col_p, col_i, col_c = st.columns(3)
    with col_p: show_tasks_by_status(TaskStatus.PENDING)
    with col_i: show_tasks_by_status(TaskStatus.IN_PROGRESS)
    with col_c: show_tasks_by_status(TaskStatus.COMPLETED)

# -----------------------------
# App
# -----------------------------
def main():
    st.set_page_config(page_title="To Do App", page_icon="📝", layout="centered")
    st.header("To Do App")
    show_add_form()
    show_tasks()

if __name__ == "__main__":
    main()
