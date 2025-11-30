import frappe


def update_employee_check_in_times(employee, checkin_time):
    """Update Employee Consistent Check In Time and Max Consistent Check In Time"""
    from hrms.hr.doctype.shift_assignment.shift_assignment import (
        get_actual_start_end_datetime_of_shift,
    )

    if not employee:
        return
    # get the employee's shift from their assigned shifts or company default
    shift = get_actual_start_end_datetime_of_shift(employee.name, checkin_time, True)
    actual_start, actual_end = shift.get("actual_start"), shift.get("actual_end")
    if not actual_start or not actual_end:
        frappe.log(
            "No shift found for Employee: {}\nActual Start: {}\nActual End: {}".format(
                employee.name, actual_start, actual_end
            )
        )
        return
    # if user is checked before or at shift start time, increment consistent check in time
    if checkin_time <= actual_start:
        emp_cur_on_time_checkins = employee.get("consistent_on_time_checkins", 0)
        employee.set(
            "consistent_on_time_checkins",
            emp_cur_on_time_checkins + 1,
        )
        # update max consistent check in time if applicable
        employee.set(
            "max_on_time_checkins",
            max(
                employee.get("max_on_time_checkins", 0),
                emp_cur_on_time_checkins + 1,
            ),
        )
    else:
        # reset consistent check in time
        employee.set("consistent_on_time_checkins", 1)

    try:
        frappe.flags.ignore_permissions = True
        employee.db_update()
    except Exception as e:
        frappe.log_error(
            "Employee Check-in Time Update Error",
            "Failed to update check-in times for Employee {}. Reason:\n{}".format(
                employee.name, frappe.get_traceback()
            ),
            reference_doctype="Employee",
            reference_name=employee.name,
        )


def check_in_employee(login_user, checkin_time):
    employee_check_in, employee = _auto_check_in(
        login_user, checkin_type="IN", time=checkin_time
    )
    if not employee_check_in:
        frappe.log_error(
            "Employee Auto Check-in Error",
            "Check-in could not be performed for User: {}\nDetails: {}".format(
                login_user, {"employee": employee, "checkin_time": checkin_time}
            ),
        )
        return
    try:
        employee_check_in.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.log("Employee checked in")
    except:
        frappe.log_error(
            "Employee Auto Check-in Error",
            "Check-in for Employee {} failed, Reason\n{}".format(
                employee, frappe.get_traceback()
            ),
            reference_doctype="Employee",
            reference_name=employee.name,
        )


def check_out_employee(login_user, checkin_time):
    employee_check_in, employee = _auto_check_in(
        login_user, checkin_type="OUT", time=checkin_time
    )
    if not employee_check_in:
        frappe.log_error(
            "Employee Auto Check-out Error",
            "Check-out could not be performed for User: {}\nDetails: {}".format(
                login_user, {"employee": employee, "checkin_time": checkin_time}
            ),
        )
        return
    try:
        employee_check_in.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.log("Employee checked out")
    except:
        frappe.log_error(
            "Employee Auto Check-out Error",
            "Check-out for Employee {} failed, Reason\n{}".format(
                employee, frappe.get_traceback()
            ),
            reference_doctype="Employee",
            reference_name=employee.name,
        )


def _auto_check_in(login_user, checkin_type: str, time):
    if not login_user:
        return (None, None)
    if login_user == "Guest":
        return (None, None)
    if "System Manager" in frappe.get_roles(login_user):
        frappe.error_log(
            "Employee Auto Check-in Skipped",
            "System Manager User: {}\nWith Roles: {}".format(
                login_user, frappe.get_roles(login_user)
            ),
        )
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
    employee_check_in.set("time", time)
    employee_check_in.set("log_type", checkin_type)
    return employee_check_in, employee
