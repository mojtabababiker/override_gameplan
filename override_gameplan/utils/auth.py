import frappe
from frappe.auth import LoginManager
from frappe.utils import now_datetime

from .employee_checkins import (
    update_employee_check_in_times,
)


def on_login(login_manager: LoginManager):
    """Function that runs on user login and performs:
    * Enqueue Employee Auto Check-in
    * Update Employee Consistent Check In Time (if applicable)
    * Update Employee Max Consistent Check In Time (if applicable)
    """
    checkin_time = now_datetime()
    employee = frappe.get_doc(
        "Employee", {"user_id": login_manager.user, "status": "Active"}
    )
    if not employee:
        frappe.log_error(
            "Employee Auto Check-in Error",
            "No active Employee found for User: {}".format(login_manager.user),
        )
        return
    # enqueue auto check-in
    frappe.enqueue(
        "override_gameplan.utils.employee_checkins.check_in_employee",
        queue="short",
        enqueue_after_commit=True,
        login_user=login_manager.user,
        checkin_time=checkin_time,
    )

    # update Employee Consistent Check In Time
    update_employee_check_in_times(employee, checkin_time)


def on_logout(login_manager: LoginManager):
    """Function that runs on user logout and performs:
    * Enqueue Employee Auto Check-out
    """
    frappe.enqueue(
        "override_gameplan.utils.employee_checkins.check_out_employee",
        queue="short",
        enqueue_after_commit=True,
        login_user=login_manager.user,
        checkin_time=now_datetime(),
    )
