# __init__.py
# ============================================================================
# Puppet Mode - Blender Add-on for Real-Time 2D Character Puppeteering
# ============================================================================
#
# This add-on recreates Adobe Character Animator workflow in Blender:
# - 2D Grease Pencil characters with armature rigs
# - Rig-first workflow: skeleton exists immediately as drawing guide
# - Body part selection UI for organized drawing
# - Rotation views for replacement-style animation
# - Real-time performance via OSC input (future phases)
#
# Inspired by:
# - Adobe Character Animator
# - After Effects Duik
# - Blender Studio's "Impulse Purchase" OK Go music video
#
# ============================================================================

bl_info = {
    "name": "Puppet Mode",
    "author": "Your Name",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Puppet Mode",
    "description": "Real-time 2D character puppeteering with Grease Pencil",
    "warning": "Early development - Phase 1",
    "doc_url": "",
    "category": "Animation",
}


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

import bpy

# Import submodules
# Note: We use relative imports because this is a package
from . import constants
from .operators import operator_classes
from .operators.create_puppet import PUPPET_OT_create_puppet
from .panels import panel_classes
from .panels.main_panel import PUPPET_PT_main_panel, PUPPET_OT_select_gp


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

# Collect all classes that need to be registered
classes = [
    # Operators
    PUPPET_OT_create_puppet,
    PUPPET_OT_select_gp,
    # Panels
    PUPPET_PT_main_panel,
]


def register():
    """Register all add-on classes with Blender."""
    for cls in classes:
        bpy.utils.register_class(cls)

    print(f"Puppet Mode v{'.'.join(map(str, bl_info['version']))} registered")


def unregister():
    """Unregister all add-on classes from Blender."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    print("Puppet Mode unregistered")


# ----------------------------------------------------------------------------
# DEVELOPMENT: Allow running as script for quick testing
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    register()
