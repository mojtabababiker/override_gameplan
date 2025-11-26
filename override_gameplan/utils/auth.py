import frappe
from frappe.auth import LoginManager
from frappe.utils import now_datetime


def on_login(login_manager: LoginManager):
    """Function that runs on user login and performs:
    * Employee Auto Check-in"""
    # print("Login Hook Triggered")
    employee_check_in, employee = auto_check_in(login_manager.user, checkin_type="IN")
    if not employee_check_in:
        return
    try:
        employee_check_in.insert(ignore_permissions=True)
        frappe.log("Employee checked in")
    except:
        frappe.log_error(
            "Employee Auto Check-in Error",
            "Check-in for Employee {} failed, Reason\n{}".format(
                employee, frappe.errprint(frappe.get_traceback())
            ),
            reference_doctype="Employee",
            reference_name=employee.name,
        )


def on_logout(login_manager: LoginManager):
    # print("Logout Hook Triggered")
    employee_check_in, employee = auto_check_in(login_manager.user, checkin_type="OUT")
    if not employee_check_in:
        return
    try:
        employee_check_in.insert(ignore_permissions=True)
        frappe.log("Employee checked out")
    except:
        frappe.log_error(
            "Employee Auto Check-out Error",
            "Check-out for Employee {} failed, Reason\n{}".format(
                employee, frappe.errprint(frappe.get_traceback())
            ),
            reference_doctype="Employee",
            reference_name=employee.name,
        )


def auto_check_in(login_user, checkin_type: str):
    print("Auto Check-in Hook Triggered")
    print("Login User:", login_user)
    if not login_user:
        return (None, None)
    # user = frappe.get_doc("User", login_user)
    if login_user == "Guest":
        return (None, None)
    if "System Manager" in frappe.get_roles():
        print("System Manager logged in, skipping Employee checkin.")
        return (None, None)
    employee = frappe.get_value(
        "Employee", {"user_id": login_user, "status": "Active"}, "name"
    )
    if not employee:
        frappe.log_error(
            "Employee Auto Check-in Error",
            "No active Employee found for User: {}".format(login_user),
        )
        return (None, None)
    # auto check-in employee
    employee_check_in = frappe.new_doc("Employee Checkin")
    employee_check_in.set("employee", employee)
    employee_check_in.set("time", now_datetime())
    employee_check_in.set("log_type", checkin_type)
    return employee_check_in, employee
