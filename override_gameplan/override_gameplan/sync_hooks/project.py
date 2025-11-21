"""Module that sync between Gameplane projects and Projects."""

import frappe


MAPPED_FIELDS = {
    "project_name": "project_name",
    "notes": "description",
    "users": "members",
    "_assign": "admin",
}


def create_project(doc, method=None):
    """Create a Gameplane project when a new Project is created.
    Mapping:
        doc Project Name -> project Title
        doc Notes -> project Description
        doc Users -> project Members
        doc _assign -> project Admin
    """
    frappe.msgprint(
        "Creating Gameplane project for Project: {}".format(doc.name), alert=True
    )
    frappe.log("Creating Gameplane project for Project: {}".format(doc))
    try:
        gp_project = frappe.get_doc(
            {
                "doctype": "GP Project",
                "title": doc.project_name,
                "description": doc.notes,
                "members": [
                    {
                        "user": (
                            r.user
                            if hasattr(r, "user")
                            else r.get("user") if isinstance(r, dict) else None
                        )
                    }
                    for r in (doc.get("users") or [])
                    if (hasattr(r, "user") and r.user)
                    or (isinstance(r, dict) and r.get("user"))
                ],
                "is_private": 1,
                # "team":
            }
        )
        # adding the admin from the first assign if available
        if hasattr(doc, "_assign") and doc._assign and len(doc._assign) > 0:
            first_assign = frappe.parse_json(doc._assign)[0]
            gp_project.admin = first_assign
            gp_project.append("members", {"user": first_assign})

        # adding gamepaln members from the project users
        for row in doc.get("users", []):
            user = _extract_user(row)
            if user:
                gp_project.append("members", {"user": user})

        # if there is a customer for the project then we need to add the GP project in the customer team (category)
        if hasattr(doc, "customer") and doc.customer:
            try:
                gp_team = frappe.get_doc("GP Team", {"name": doc.customer})
                gp_project.set("team", gp_team.name)
            except frappe.DoesNotExistError:
                # TODO: create the GP team
                frappe.msgprint(
                    "Current project Customer {} has no Gameplan category (team), falling to ungategorized".format(
                        doc.customer
                    ),
                    alert=True,
                    indicator="orange",
                )

        gp_project.insert(ignore_permissions=True)
        frappe.msgprint(
            "Created Gameplane project for Project: {}".format(doc.name),
            alert=True,
            indicator="green",
        )
    except Exception as e:
        frappe.log_error(
            "Error creating Gameplane project for Project {}: {}\n{}".format(
                doc.name, str(e), frappe.get_traceback()
            ),
            "Gameplane Project Creation Error",
        )
        frappe.msgprint(
            "Failed to create Gameplane project for Project: {}. Check error log for details.".format(
                doc.name
            ),
            alert=True,
            indicator="red",
        )


def on_project_update(doc, method):
    """Update the corresponding Gameplane project when a Project is updated."""
    # the case when the corresponding GP Project is not exists
    if not frappe.db.exists("GP Project", {"title": doc.project_name}):
        return create_project(doc=doc)

    gp_project = frappe.get_doc("GP Project", {"title": doc.project_name})

    scalar_fields = [f for f in MAPPED_FIELDS.keys() if f != "users"]
    scalar_changed = any(doc.has_value_changed(field) for field in scalar_fields)

    # build source users and target members simple lists for comparison
    src_users = [_extract_user(r) for r in (doc.get("users") or [])]
    src_users = [u for u in src_users if u]  # filter out empty values
    tgt_members = [_extract_user(r) for r in (gp_project.get("members") or [])]
    tgt_members = [u for u in tgt_members if u]  # filter out empty values

    # when there is no change in mapped scalar fields and members childtable, do nothing
    if not scalar_changed and set(src_users) == set(tgt_members):
        return
    try:
        for project_field, gp_field in MAPPED_FIELDS.items():
            # special handling for users -> members childtable mapping
            if project_field == "users" and gp_field == "members":
                # replace members with mapped minimal rows containing only the user link
                gp_project.set("members", [])
                for row in doc.get("users") or []:
                    user_val = _extract_user(row)
                    if user_val:
                        gp_project.append("members", {"user": user_val})
                continue

            if project_field == "_assign" and gp_field == "admin":
                # set the admin from the first assign if available
                gp_project.admin = None
                if hasattr(doc, "_assign") and doc._assign and len(doc._assign) > 0:
                    first_assign = frappe.parse_json(doc._assign)[0]
                    gp_project.admin = first_assign
                continue

            gp_project.set(gp_field, doc.get(project_field), as_value=True)
        gp_project.save()
    except Exception as e:
        frappe.log_error(
            "Error updating Gameplane project for Project {}: {}\n{}".format(
                doc.name, str(e), frappe.get_traceback()
            ),
            "Gameplane Project Update Error",
        )
        frappe.msgprint(
            "Failed to update Gameplane project for Project: {}. Check error log for details.".format(
                doc.name
            ),
            alert=True,
            indicator="red",
        )


def on_project_trash(doc, method):
    """Delete the corresponding Gameplane project when a Project is deleted."""
    try:
        gp_project = frappe.get_doc("GP Project", {"title": doc.project_name})

        if gp_project:
            gp_project.delete()
    except frappe.DoesNotExistError:
        return
    except Exception as e:
        frappe.log_error(
            "Error deleting Gameplane project for Project {}: {}\n{}".format(
                doc.name, str(e), frappe.get_traceback()
            ),
            "Gameplane Project Deletion Error",
        )


def _extract_user(row):
    try:
        if hasattr(row, "get") and callable(getattr(row, "get")):
            # row might be a Document row with get
            return row.get("user") or row.get("member")
        if hasattr(row, "user"):
            return getattr(row, "user")
        if isinstance(row, dict):
            return row.get("user") or row.get("member")
    except Exception:
        return None
    return None
