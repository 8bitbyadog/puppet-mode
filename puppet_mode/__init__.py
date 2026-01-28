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
    "author": "8bitbyadog",
    "version": (0, 2, 0),  # Phase 1c
    "blender": (4, 0, 0),  # Minimum version; tested on 5.0
    "location": "View3D > Sidebar > Puppet Mode",
    "description": "Real-time 2D character puppeteering with Grease Pencil",
    "warning": "Early development - Phase 1c",
    "doc_url": "https://github.com/8bitbyadog/puppet-mode",
    "category": "Animation",
}


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

import bpy

# Import submodules
from . import constants
from .core import properties
from .core import rig_builder

# Import classes for registration
from .operators.create_puppet import PUPPET_OT_create_puppet
from .operators.draw_part import (
    PUPPET_OT_view_part,
    PUPPET_OT_draw_part,
    PUPPET_OT_set_rotation,
    PUPPET_OT_toggle_onion,
)
from .panels.main_panel import (
    PUPPET_PT_main_panel,
    PUPPET_OT_select_puppet,
    PUPPET_OT_select_gp,
)


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

# Collect all classes that need to be registered
classes = [
    # Operators
    PUPPET_OT_create_puppet,
    PUPPET_OT_view_part,
    PUPPET_OT_draw_part,
    PUPPET_OT_set_rotation,
    PUPPET_OT_toggle_onion,
    PUPPET_OT_select_puppet,
    PUPPET_OT_select_gp,
    # Panels
    PUPPET_PT_main_panel,
]


def register():
    """Register all add-on classes with Blender."""
    # Register properties first (they're needed by panels)
    properties.register()

    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

    print(f"Puppet Mode v{'.'.join(map(str, bl_info['version']))} registered")


def unregister():
    """Unregister all add-on classes from Blender."""
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Unregister properties last
    properties.unregister()

    print("Puppet Mode unregistered")


# ----------------------------------------------------------------------------
# DEVELOPMENT: Allow running as script for quick testing
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    register()
