import frappe
import gameplan


def create_user_profile(doc, method=None):
    if not frappe.db.exists("GP User Profile", {"user": doc.name}):
        print("\n\nCreating GP User Profile for user:", doc.name, end="\n\n")
        # handle case where user profile does not exist - which should not happen normally: This method is called after the gameplan.gameplan.doctype.gp_user_profile.create_user_profile
        frappe.get_doc(
            "GP User Profile",
            {
                "user": doc.name,
                "full_name": f"{doc.first_name}{' ' + doc.middle_name if doc.middle_name else ''} {doc.last_name}".strip(),
                "enabled": doc.enabled,
                "bio": doc.bio,
                "image": doc.user_image,
            },
        ).insert(ignore_permissions=True)
        frappe.db.commit()
        print("GP User Profile created and committed to the database.")

    if "Gameplan Member" not in doc.get("roles"):
        print("\n\nAdding 'Gameplan Member' role to user:", doc.name, end="\n\n")
        # add GP Member role to the user
        doc.flags.ignore_permissions = True
        doc.add_roles("Gameplan Member")
        doc.save()
        print("'Gameplan Member' role added and user saved.")
    gameplan.refetch_resource("Users")


def on_user_update(doc, method=None):
    sync_fields = ["full_name", "enabled", "bio", "user_image"]
    if any(doc.has_value_changed(field) for field in sync_fields):
        profile = frappe.get_doc("GP User Profile", {"user": doc.name})
        profile.enabled = doc.enabled
        profile.full_name = f"{doc.first_name}{' ' + doc.middle_name if doc.middle_name else ''} {doc.last_name}".strip()
        profile.bio = doc.bio
        if doc.has_value_changed("user_image"):
            profile.image = doc.user_image
            gameplan.refetch_resource("Users")
        profile.save(ignore_permissions=True)
