import frappe

from ..setup import delete_custom_fields


def execute():
    """Remove 'last_updated_by' field from ERPNext Task doctype."""
    try:
        delete_custom_fields(fields_to_delete={"Task": ["last_updated_by"]})
    except Exception as e:
        frappe.log_error(
            message=f"Error deleting custom field 'last_updated_by' for Task: {str(e)}\n\n{frappe.get_traceback()}",
            title="Custom Field Deletion Error",
            reference_doctype="Task",
        )
    frappe.db.commit()
    frappe.clear_cache()
