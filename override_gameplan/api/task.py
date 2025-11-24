import frappe


@frappe.whitelist()
def create_project_task_from_gp_task(taskDoc=None):
    """Create a Project Task in Frappe when a GamePlan Task is created."""
    doc = taskDoc or frappe.request.get_json()
    # print("\n\nReceived GP Task data:", doc, end="\n\n")
    if not doc.get("title", None):
        frappe.throw("Title is required to create a Project Task.")
    task = frappe.new_doc(
        "Task",
        last_updated_by="GP",
        subject=doc.get("title"),
    )

    task = set_task_fields(task, doc)

    project = get_project(doc)
    if project:
        task.set("project", project)
    try:
        # print("\n\nCreating Project Task with data:", task.as_dict(), end="\n\n")
        task.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(
            f"Project Task '{task.subject}' created from GP Task '{doc.get('title')}'",
            alert=True,
            indicator="green",
        )
        return task
    except Exception as e:
        frappe.log_error(
            message=f"Error creating Project Task from GP Task {doc.get('title')}: {str(e)}\n\n{frappe.get_traceback()}",
            title="Project Task Creation Error",
            reference_doctype="Task",
        )


@frappe.whitelist()
def update_project_task_from_gp_task():
    """Update a Project Task in Frappe when a GamePlan Task is updated."""
    doc = frappe.request.get_json()
    if not doc.get("title", None):
        frappe.throw("Title is required to update a Project Task.")

    project = get_project(doc)
    if not frappe.db.exists("Task", {"subject": doc.get("title"), "project": project}):
        return create_project_task_from_gp_task(doc)
    task = frappe.get_doc("Task", {"subject": doc.get("title"), "project": project})
    task = set_task_fields(task, doc)
    try:
        task.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(
            f"Project Task '{task.subject}' updated from GP Task '{doc.get('title')}'",
            alert=True,
            indicator="green",
        )
        return task
    except Exception as e:
        frappe.log_error(
            message=f"Error updating Project Task from GP Task {doc.get('title')}: {str(e)}\n\n{frappe.get_traceback()}",
            title="Project Task Update Error",
            reference_doctype="Task",
        )


def set_task_fields(task, doc):
    task.update(
        {
            "description": doc.get("description"),
            "assigned_to": doc.get("assigned_to"),
            "status": doc.get("status"),
            "priority": doc.get("priority"),
            "exp_start_date": doc.get("start_date"),
            "exp_end_date": doc.get("due_date"),
            "completed_on": doc.get("completed_at"),
            "completed_by": doc.get("completed_by"),
        }
    )
    return task


def get_project(doc):
    if doc.get("project"):
        gp_project = frappe.get_value(
            "GP Project", {"name": doc.get("project")}, "title"
        )
        project = frappe.get_value("Project", {"project_name": gp_project}, "name")
        return project
    return None
