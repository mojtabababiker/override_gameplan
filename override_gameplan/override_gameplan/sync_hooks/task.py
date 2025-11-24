"""Module that handle the process of syncing between projects tasks in ERPNext and GP Tasks"""

from datetime import datetime

import frappe

MAPPED_FIELDS = {
    "subject": "title",
    "project": "project",
    "status": "status",
    "assigned_to": "assigned_to",
    "priority": "priority",
    "exp_start_date": "start_date",
    "exp_end_date": "due_date",
    "description": "description",
    "completed_on": "completed_at",
    "completed_by": "completed_by",
}


def create_gp_task_from_project_task(doc, method=None):
    """Create a GP Task from a Project Task
    This function is triggered when a Project Task is created. nad create the GP Task by mapping:
    - Subject -> Title
    - Project -> GP Project
    - Status -> Status
    - Assigned To -> Assigned To
    - Priority -> Priority
    - Expected Start Date (exp_start_date) -> Start Date
    - Excepted End Date (exp_end_date) -> Due Date
    - Description -> Description
    - Completed On -> Completed At
    - Completed By -> Completed By
    - Doc Status is Completed -> Is Completed
    """
    # check to see if the last updated on is GP, if so, skip the update to avoid circular updates
    if hasattr(doc, "last_updated_by") and doc.last_updated_by == "GP":
        return
    # getting the basic fields from the Project Task
    gp_task = frappe.new_doc(
        "GP Task",
        title=doc.subject,
    )
    gp_task = _update_task_field_mapping(doc, gp_task)
    gp_task = _update_task_project(doc, gp_task)
    gp_task = _update_task_dates(doc, gp_task)
    gp_task = _update_task_completion(doc, gp_task)

    if hasattr(doc, "_assign") and doc._assign:
        gp_task.set("assigned_to", frappe.parse_json(doc._assign)[0])

    try:
        gp_task.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(
            f"GP Task '{gp_task.title}' created from Project Task '{doc.subject}'",
            alert=True,
            indicator="green",
        )
        return gp_task
    except Exception as e:
        frappe.log_error(
            message=f"Error creating GP Task from Project Task {doc.name}: {str(e)}\n\n{frappe.get_traceback()}",
            title="GP Task Creation Error",
            reference_doctype="GP Task",
        )


def update_gp_task_from_project_task(doc, method=None):
    # check to see if the last updated on is GP, if so, skip the update to avoid circular updates
    if hasattr(doc, "last_updated_by") and doc.last_updated_by == "GP":
        return
    if not frappe.db.exists("GP Task", {"title": doc.subject}):
        return create_gp_task_from_project_task(doc, method)

    if any(doc.has_value_changed(field) for field in MAPPED_FIELDS.keys()):
        gp_task = frappe.get_doc("GP Task", {"title": doc.subject})
        if any(
            doc.has_value_changed(mapped_filed)
            for mapped_filed in [
                "subject",
                "status",
                "assigned_to",
                "priority",
                "description",
            ]
        ):
            gp_task = _update_task_field_mapping(doc, gp_task)
        if doc.has_value_changed("project"):
            gp_task = _update_task_project(doc, gp_task)
        if any(
            doc.has_value_changed(date_field)
            for date_field in ["exp_start_date", "exp_end_date"]
        ):
            gp_task = _update_task_dates(doc, gp_task)
        if any(
            doc.has_value_changed(completion_field)
            for completion_field in ["status", "completed_on", "completed_by"]
        ):
            gp_task = _update_task_completion(doc, gp_task)
        try:
            # update the last updated on filed to be GP
            gp_task.save(ignore_permissions=True)
            doc.set("last_updated_on", "GP")
            frappe.db.commit()
            frappe.msgprint(
                f"GP Task '{gp_task.title}' updated from Project Task '{doc.subject}'",
                alert=True,
                indicator="green",
            )
        except Exception as e:
            frappe.log_error(
                message=f"Error updating GP Task '{gp_task.title}' from Project Task '{doc.name}': {str(e)}\n\n{frappe.get_traceback()}",
                title="GP Task Update Error",
                reference_doctype="GP Task",
            )


def delete_gp_task(doc, method=None):
    """Delete the GP Task linked to the Project Task when the Project Task is deleted"""
    if frappe.db.exists("GP Task", {"title": doc.subject}):
        gp_task = frappe.get_doc("GP Task", {"title": doc.subject})
        try:
            gp_task.delete()
            frappe.db.commit()
            frappe.msgprint(
                f"GP Task '{gp_task.title}' deleted as the linked Project Task '{doc.subject}' was deleted.",
                alert=True,
                indicator="green",
            )
        except Exception as e:
            frappe.log_error(
                message=f"Error deleting GP Task '{gp_task.title}' linked to Project Task '{doc.subject}': {str(e)}\n\n{frappe.get_traceback()}",
                title="GP Task Deletion Error",
                reference_doctype="GP Task",
            )


def assign_gp_task_to_user(doc, method=None):
    """Assign the GP Task to the same user as the Project Task"""

    if not frappe.db.exists("GP Task", {"title": doc.subject}):
        create_gp_task_from_project_task(doc, method)
        frappe.msgprint(
            f"GP Task '{gp_task.title}' assigned to user from Project Task '{doc.subject}'",
            alert=True,
            indicator="green",
        )
        return

    frappe.msgprint(
        f"Assigning GP Task linked to Project Task '{doc.subject}' to user...",
        alert=True,
        indicator="blue",
    )
    gp_task = frappe.get_doc("GP Task", {"title": doc.subject})
    if hasattr(doc, "_assign") and doc._assign:
        gp_task.set("assigned_to", frappe.parse_json(doc._assign)[0])
        try:
            gp_task.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(
                f"GP Task '{gp_task.title}' assigned to user from Project Task '{doc.subject}'",
                alert=True,
                indicator="green",
            )
        except Exception as e:
            frappe.log_error(
                message=f"Error assigning GP Task '{gp_task.title}' from Project Task '{doc.name}': {str(e)}\n\n{frappe.get_traceback()}",
                title="GP Task Assignment Error",
                reference_doctype="GP Task",
            )


def _update_task_field_mapping(doc, gp_task):
    """Update the GP Task fields based on the Project Task fields using a predefined mapping."""
    field_mapping = {
        "subject": "title",
        "status": "status",
        "assigned_to": "assigned_to",
        "priority": "priority",
        "description": "description",
    }
    for proj_field, gp_field in field_mapping.items():
        if hasattr(doc, proj_field):
            gp_task.set(gp_field, getattr(doc, proj_field))
    return gp_task


def _update_task_project(doc, gp_task):
    # checking and mapping the project
    if hasattr(doc, "project") and doc.project:
        # getting the GP Project linked to the ERPNext Project
        tsk_project = frappe.get_value("Project", {"name": doc.project}, "project_name")

        gp_project = frappe.get_value("GP Project", {"title": tsk_project}, "name")
        if gp_project:
            gp_task.set("project", gp_project)
    return gp_task


def _update_task_dates(doc, gp_task):
    """Update the GP Task dates based on the Project Task dates."""
    # mapping the dates
    if hasattr(doc, "exp_start_date") and doc.exp_start_date:
        gp_task.set("start_date", doc.exp_start_date)
    if hasattr(doc, "exp_end_date") and doc.exp_end_date:
        gp_task.set("due_date", doc.exp_end_date)

    return gp_task


def _update_task_completion(doc, gp_task):
    """Update the GP Task completion fields based on the Project Task completion fields."""
    # mapping the completion fields
    if hasattr(doc, "status") and doc.status == "Completed":
        gp_task.set("is_completed", True)
        if hasattr(doc, "completed_on") and doc.completed_on:
            gp_task.set("completed_at", datetime.date(doc.completed_on))
        if hasattr(doc, "completed_by") and doc.completed_by:
            gp_task.set("completed_by", doc.completed_by)
    else:
        gp_task.set("is_completed", False)
    return gp_task
