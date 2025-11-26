import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from .override_gameplan.custom_fields import custom_fields


def setup_custom_fields():
    """Create custom fields for specified doctypes."""
    print("\n\nSetting up custom fields...", end="\n\n")
    for doctype, fields in custom_fields.items():
        for field in fields:
            create_custom_field(doctype, field)


def delete_custom_fields(fields_to_delete=None):
    """Delete custom fields for specified doctypes."""
    print("\n\nDeleting custom fields...", end="\n\n")
    custom_fields_to_delete = fields_to_delete or custom_fields
    for doctype, fields in custom_fields_to_delete.items():
        for field in fields:
            fieldname = field.get("fieldname")
            frappe.db.delete(
                "Custom Field",
                {"dt": doctype, "fieldname": fieldname},
            )
            print(f"Deleted custom field '{fieldname}' from doctype '{doctype}'")
        frappe.clear_cache(doctype)
    print("\n\nCustom fields deletion completed.", end="\n\n")
