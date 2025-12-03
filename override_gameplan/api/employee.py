import frappe


@frappe.whitelist()
def get_employee_continuous_checkins(employee_name: str = None):
    """Fetch continuous check-in days for an employee."""
    if not employee_name:
        employee_name = frappe.get_value("Employee", {"user_id": frappe.session.user})
    if not employee_name:
        return 0

    employee = frappe.get_doc("Employee", employee_name, as_dict=True)
    on_time_checkins = employee.get("consistent_on_time_checkins", 0)
    max_strikes = employee.get("max_on_time_checkins", 0)
    return {
        "employee": (
            employee.get("first_name") + " " + employee.get("last_name")
        ).strip(),
        "continuousCheckinDays": on_time_checkins,
        "maxStrikes": max_strikes,
    }
