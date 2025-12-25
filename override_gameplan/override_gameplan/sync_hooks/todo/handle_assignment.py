"""Hook on ToDo assignment to inject the related extensions hooks"""

import frappe

from ..task import assign_gp_task_to_user
from ..team import on_customer_update
from ..project import on_project_update


MONITORED_DOCTYPES_HOOKS: dict[str, list[callable]] = {
    "Customer": [on_customer_update],
    "Project": [on_project_update],
    "Task": [assign_gp_task_to_user],
}


def handle_assignment(doc, method=None):
    """This function is used to check"""
    # when a ToDo is updated to cancelled, we trigger the on_update hooks of the referenced documents, otherwise we do nothing
    if doc.reference_type in MONITORED_DOCTYPES_HOOKS:
        ref_doc = frappe.get_doc(doc.reference_type, doc.reference_name)
        for hook in MONITORED_DOCTYPES_HOOKS[doc.reference_type]:
            hook(ref_doc, method="on_update")


def handle_assignment_removal(doc, method=None):
    """This function is used to check"""
    if not doc.has_value_changed("status"):
        return
    if doc.status != "Cancelled":
        return
    if doc.reference_type in MONITORED_DOCTYPES_HOOKS:
        for hook in MONITORED_DOCTYPES_HOOKS[doc.reference_type]:
            ref_doc = frappe.get_doc(doc.reference_type, doc.reference_name)
            hook(ref_doc, method="on_update")
