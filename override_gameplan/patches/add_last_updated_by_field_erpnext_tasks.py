import frappe


def execute():
    """Add 'last_updated_by' field to ERPNext Task doctype with GP as default."""
    tasks = frappe.get_all("Task", fields=["name"])
    for task in tasks:
        try:
            frappe.db.set_value("Task", task.name, "last_updated_by", "GP")
        except Exception as e:
            frappe.log_error(
                message=f"Error updating 'last_updated_by' for Task {task.name}: {str(e)}\n\n{frappe.get_traceback()}",
                title="Task Update Error",
                reference_doctype="Task",
            )
    frappe.db.commit()
