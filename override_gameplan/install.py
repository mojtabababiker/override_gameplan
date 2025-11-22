import os
from os import path
import frappe

from override_gameplan.setup import setup_custom_fields


def before_install():
    pass


def after_install():
    """Setup doctype customizations after installation."""
    setup_custom_fields()
    frappe.db.commit()
    frappe.clear_cache()
    # build frontend app
    print("\n\nBuilding Frontend App...", end="\n\n")
    os.system(
        f"pwd && cd {path.join(path.dirname(__file__), '../frontend')} && pnpm build"
    )
