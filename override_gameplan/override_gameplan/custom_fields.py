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
    ]
}
