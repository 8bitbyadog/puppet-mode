# operators/create_puppet.py
# ============================================================================
# Operator for creating a new puppet.
# This is the main "Create New Puppet" button functionality.
# ============================================================================

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from ..core.rig_builder import create_puppet, get_puppets_in_scene
from ..constants import get_total_drawable_parts


class PUPPET_OT_create_puppet(Operator):
    """Create a new puppet with armature and Grease Pencil layers"""

    bl_idname = "puppet.create_puppet"
    bl_label = "Create New Puppet"
    bl_description = "Create a new puppet with full rig and drawing layers"
    bl_options = {'REGISTER', 'UNDO'}

    # Optional: Allow user to specify a custom name
    puppet_name: StringProperty(
        name="Name",
        description="Name for the new puppet",
        default="Puppet"
    )

    def execute(self, context):
        """Execute the operator - create the puppet."""
        try:
            # Create the puppet (armature + parts collection)
            armature_obj = create_puppet(context, self.puppet_name)

            # Report success
            total_parts = get_total_drawable_parts()
            self.report(
                {'INFO'},
                f"Created puppet '{armature_obj['puppet_name']}' "
                f"with {total_parts} drawable parts"
            )

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to create puppet: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        """
        Invoke the operator - show a dialog for name input.
        For quick creation, use execute directly.
        """
        # For now, skip the dialog and create directly
        # In future, could use: return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

def register():
    bpy.utils.register_class(PUPPET_OT_create_puppet)


def unregister():
    bpy.utils.unregister_class(PUPPET_OT_create_puppet)
