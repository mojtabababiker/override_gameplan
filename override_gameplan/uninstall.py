import frappe

from override_gameplan.setup import delete_custom_fields


def after_uninstall():
    """Cleanup actions after uninstalling the app."""
    delete_custom_fields()
    frappe.db.commit()
    frappe.clear_cache()
