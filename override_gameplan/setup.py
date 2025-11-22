import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from .override_gameplan.custom_fields import custom_fields


def setup_custom_fields():
    """Create custom fields for specified doctypes."""
    print("\n\nSetting up custom fields...", end="\n\n")
    for doctype, fields in custom_fields.items():
        for field in fields:
            create_custom_field(doctype, field)


def delete_custom_fields():
    """Delete custom fields for specified doctypes."""
    print("\n\nDeleting custom fields...", end="\n\n")
    for doctype, fields in custom_fields.items():
        for field in fields:
            fieldname = field.get("fieldname")
            if fieldname and frappe.db.exists(
                "Custom Field", {"dt": doctype, "fieldname": fieldname}
            ):
                frappe.delete_doc(
                    "Custom Field", {"dt": doctype, "fieldname": fieldname}, force=True
                )
