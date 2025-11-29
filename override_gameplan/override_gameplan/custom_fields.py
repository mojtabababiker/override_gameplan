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
    ],
    "Employee": [
        {
            "fieldname": "consistent_on_time_checkins",
            "label": _("Consistent On Time Check-ins (Days)"),
            "description": _(
                "Number of days the employee has checked in on time consistently."
            ),
            "fieldtype": "Int",
            "insert_after": "attendance_device_id",
            "perm_level": 1,
            "in_list_view": 1,
            "read_only": 1,
            "default": 0,
        },
        {
            "fieldname": "max_on_time_checkins",
            "label": _("Max On Time Check-ins (Days)"),
            "description": _(
                "Maximum number of days for consistent on-time check-ins."
            ),
            "fieldtype": "Int",
            "insert_after": "consistent_on_time_checkins",
            "perm_level": 1,
            "in_list_view": 1,
            "read_only": 1,
            "default": 0,
        },
    ],
}
