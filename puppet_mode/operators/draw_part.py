# operators/draw_part.py
# ============================================================================
# Operator for activating a specific body part layer and entering Draw mode.
# This is the "Draw This View" button functionality.
# ============================================================================

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from ..core.properties import get_current_layer_name


class PUPPET_OT_draw_part(Operator):
    """Activate the selected body part layer and enter Grease Pencil Draw mode"""

    bl_idname = "puppet.draw_part"
    bl_label = "Draw This View"
    bl_description = "Activate this layer and start drawing"
    bl_options = {'REGISTER', 'UNDO'}

    # Optional: allow specifying layer directly (for rotation grid buttons)
    layer_name: StringProperty(
        name="Layer Name",
        description="Specific layer to activate (optional)",
        default="",
    )

    @classmethod
    def poll(cls, context):
        """Check if we can execute (need an active puppet)."""
        obj = context.active_object
        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            return True
        if obj and obj.type == 'GPENCIL' and obj.get("puppet_rig"):
            return True
        return False

    def execute(self, context):
        """Activate the layer and enter draw mode."""
        # Find the GP object
        gp_obj = self._get_gp_object(context)
        if not gp_obj:
            self.report({'ERROR'}, "No puppet GP object found")
            return {'CANCELLED'}

        # Determine which layer to activate
        if self.layer_name:
            layer_name = self.layer_name
        else:
            layer_name = get_current_layer_name(context)

        # Find and activate the layer
        gp_data = gp_obj.data
        layer = gp_data.layers.get(layer_name)

        if not layer:
            self.report({'WARNING'}, f"Layer '{layer_name}' not found")
            return {'CANCELLED'}

        # Make the layer visible and active
        layer.hide = False
        gp_data.layers.active = layer

        # Select the GP object and make it active
        for obj in bpy.data.objects:
            obj.select_set(False)
        gp_obj.select_set(True)
        context.view_layer.objects.active = gp_obj

        # Enter Draw mode
        # Blender 5.0+ uses PAINT_GREASE_PENCIL, older versions use PAINT_GPENCIL
        try:
            # Try Blender 5.0+ mode name first
            bpy.ops.object.mode_set(mode='PAINT_GREASE_PENCIL')
        except TypeError:
            try:
                # Fallback to older mode name
                bpy.ops.object.mode_set(mode='PAINT_GPENCIL')
            except:
                self.report({'INFO'}, f"Activated layer '{layer_name}' - enter Draw mode manually (press D)")
                return {'FINISHED'}

        self.report({'INFO'}, f"Drawing on: {layer_name}")
        return {'FINISHED'}

    def _get_gp_object(self, context):
        """Find the GP object for the active puppet."""
        obj = context.active_object

        # If GP object is selected, use it
        if obj and obj.type == 'GPENCIL' and obj.get("puppet_rig"):
            return obj

        # If armature is selected, find its GP object
        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            gp_name = obj.get("puppet_gp")
            if gp_name and gp_name in bpy.data.objects:
                return bpy.data.objects[gp_name]

        return None


class PUPPET_OT_set_rotation(Operator):
    """Set the rotation view from the visual selector"""

    bl_idname = "puppet.set_rotation"
    bl_label = "Set Rotation"
    bl_description = "Select this rotation view"
    bl_options = {'REGISTER'}

    rotation: StringProperty(
        name="Rotation",
        description="Rotation view to select",
        default="Front",
    )

    def execute(self, context):
        """Set the rotation property."""
        props = context.scene.puppet_selector
        props.rotation = self.rotation
        return {'FINISHED'}


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

classes = [
    PUPPET_OT_draw_part,
    PUPPET_OT_set_rotation,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
