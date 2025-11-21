"""A Module that handles the process of syncing ERPNext Customer with Gameplan Team (Category)
Making the GP Projects and Spaces Categorized by the Customer they belong to."""

import frappe

MAPPING_FIELDS = {
    "customer_name": "name",
    "customer_name": "title",
    "account_manager": "admin",
    "_assign": "members",
}


def create_team(doc, method=None):
    """Create GP Team when a new customer is inserted in ERPNext.
    Mapping:

        doc Customer Name -> team Name
        doc Customer Name -> team Title

        the GP Team Members will compined of the customer account manager, and all users assigned to the customer.
        The Team Will be set as Private.
    """
    if frappe.db.exists("GP Team", {"name": doc.customer_name}):
        frappe.msgprint(
            "GP Team for Customer {} already exists.".format(doc.customer_name),
            alert=True,
        )
        return
    gp_team = frappe.get_doc(
        {
            "doctype": "GP Team",
            "name": doc.customer_name,
            "title": doc.customer_name,
            "is_private": 1,
        }
    )

    gp_team = update_team_member(doc, gp_team)
    try:
        gp_team.insert(ignore_permissions=True)
        frappe.msgprint(
            "Created GP Team for Customer: {}".format(doc.customer_name),
            alert=True,
        )
    except Exception as e:
        frappe.log_error(
            "Error creating GP Team for Customer {}: {}\n{}".format(
                doc.customer_name, str(e), frappe.get_traceback()
            ),
            "GP Team Creation Error",
        )
        frappe.msgprint(
            "Error creating GP Team for Customer {}: {}".format(
                doc.customer_name, str(e)
            ),
            alert=True,
            indicator="red",
        )


def on_customer_update(doc, method=None):
    """Update GP Team when a customer is updated in ERPNext.
    Mapping:

        doc Customer Name -> team Name
    """
    if not frappe.db.exists("GP Team", {"name": doc.customer_name}):
        return create_team(doc=doc)

    if any(doc.has_value_changed(field) for field in MAPPING_FIELDS.keys()):
        gp_team = frappe.get_doc("GP Team", {"name": doc.customer_name})
        for customer_field, gp_team_field in MAPPING_FIELDS.items():
            if customer_field == "account_manager" or customer_field == "_assign":
                gp_team = update_team_member(doc, gp_team)
            else:
                gp_team.set(gp_team_field, doc.get(customer_field), as_value=True)
        try:
            gp_team.save(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(
                "Error updating GP Team for Customer {}: {}\n{}".format(
                    doc.customer_name, str(e), frappe.get_traceback()
                ),
                "GP Team Creation Error",
            )
            frappe.msgprint(
                "Error updating GP Team for Customer {}: {}".format(
                    doc.customer_name, str(e)
                ),
                alert=True,
                indicator="red",
            )


def on_customer_trash(doc, method=None):
    """Delete GP Team when a customer is trashed in ERPNext."""
    try:
        gp_team = frappe.get_doc("GP Team", {"name": doc.customer_name})
        gp_team.delete(ignore_permissions=True)

    except frappe.DoesNotExistError:
        return
    except Exception as e:
        frappe.log_error(
            "Error deleting GP Team for Customer {}: {}\n{}".format(
                doc.customer_name, str(e), frappe.get_traceback()
            ),
            "GP Team Deletion Error",
        )
        frappe.msgprint(
            "Error deleting GP Team for Customer {}: {}\n".format(
                doc.customer_name, str(e)
            ),
            alert=True,
            indicator="red",
            # primary_action={"Delete it": }
        )


def _get_team_members(doc):
    members = []
    if doc.account_manager:
        members.append(doc.account_manager)

    if hasattr(doc, "_assign") and doc._assign and len(doc._assign) > 0:
        parsed_assigns = frappe.parse_json(doc._assign)
        for assign in parsed_assigns:
            members.append(assign)
    return members


def update_team_member(doc, gp_team_doc):
    team_member = _get_team_members(doc)

    frappe.log("Team Members to set: {}".format(team_member))
    frappe.log("Current GP Team Members: {}".format(gp_team_doc.get("members")))
    # if the customer team is same as the current gp team member do nothing
    if set(team_member) == set(gp_team_doc.get("members", default=[])):
        return gp_team_doc

    gp_team_doc.set("members", [])
    for member in team_member:
        gp_team_doc.append("members", {"user": member})

    return gp_team_doc
