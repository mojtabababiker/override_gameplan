from frappe.desk.page.setup_wizard.install_fixtures import (
    _,
)

custom_fields = {
    "Task": [
        {
            "fieldname": "assigned_to",
            "label": _("Assigned To"),
            "fieldtype": "Link",
            "options": "User",
            "insert_after": "status",
            "perm_level": 1,
            "in_list_view": 1,
            "allow_in_quick_entry": 1,
        },
        {
            "fieldname": "last_updated_by",
            "label": _("Last Updated By"),
            "description": _("Used on the sync hooks to prevent infinite hooks calls."),
            "fieldtype": "Select",
            "options": "Desk\nGP",
            "insert_after": "assigned_to",
            "perm_level": 1,
            "hidden": 1,
            "no_copy": 1,
            "read_only": 1,
        },
    ]
}
