# panels/__init__.py
# ============================================================================
# Panels module for Puppet Mode.
# Contains all UI panels displayed in Blender.
# ============================================================================

from .main_panel import (
    PUPPET_PT_main_panel,
    PUPPET_OT_select_puppet,
    PUPPET_OT_select_gp,
)

# List of all panel classes to register
panel_classes = [
    PUPPET_PT_main_panel,
    PUPPET_OT_select_puppet,
    PUPPET_OT_select_gp,
]
