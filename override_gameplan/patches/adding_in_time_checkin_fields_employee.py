"""A patch that adds time check-in fields to the Employee model.
This patch adds the following fields to the Employee doctype:
 - consistent_in_time_checkins: integer field to track consistent time check-ins
 - max_in_time_checkins: integer field to set the maximum consistent time check-ins
"""

from override_gameplan.setup import setup_custom_fields


def execute():
    """
    Add time check-in fields to Employee doctype.
    """
    setup_custom_fields(
        fields_to_setup={
            "Employee": [
                {
                    "fieldname": "consistent_in_time_checkins",
                    "label": "Consistent In Time Check-ins (Days)",
                    "description": "Number of days the employee has checked in on time consistently.",
                    "fieldtype": "Int",
                    "insert_after": "attendance_device_id",
                    "perm_level": 1,
                    "in_list_view": 1,
                    "read_only": 1,
                    "default": 0,
                },
                {
                    "fieldname": "max_in_time_checkins",
                    "label": "Max In Time Check-ins (Days)",
                    "description": "Maximum number of days for consistent in-time check-ins.",
                    "fieldtype": "Int",
                    "insert_after": "consistent_in_time_checkins",
                    "perm_level": 1,
                    "in_list_view": 1,
                    "read_only": 1,
                    "default": 0,
                },
            ]
        }
    )
