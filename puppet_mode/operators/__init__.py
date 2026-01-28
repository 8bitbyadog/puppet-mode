# operators/__init__.py
# ============================================================================
# Operators module for Puppet Mode.
# Contains all Blender operators (button actions).
# ============================================================================

from .create_puppet import PUPPET_OT_create_puppet

# List of all operator classes to register
operator_classes = [
    PUPPET_OT_create_puppet,
]
