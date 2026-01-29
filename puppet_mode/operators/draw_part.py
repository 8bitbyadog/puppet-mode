# operators/draw_part.py
# ============================================================================
# Operators for viewing and drawing on specific body part layers.
# Includes: Draw This View, View This View, Set Rotation, Onion Skin Toggle
#
# PER-OBJECT ARCHITECTURE: Each body part gets its own GP object.
# This avoids Blender 5.0's GP v3 layer-switching bug where drawings
# disappear when switching active layers within a single GP object.
#
# - VIEW mode: Show ALL drawn GP objects for current view at full opacity
# - DRAW mode: Select target GP object, show others as faint reference
# - Drawings persist naturally because each GP object is independent
# ============================================================================

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from ..core.properties import (
    get_current_layer_name,
    get_view_layer_names,
)


def get_puppet_armature(context):
    """Find the puppet armature from whatever is currently selected."""
    obj = context.active_object
    gp_types = ('GPENCIL', 'GREASEPENCIL')

    if obj:
        # Direct armature selection
        if obj.type == 'ARMATURE' and obj.get("is_puppet"):
            return obj

        # GP object -> find its armature
        if obj.type in gp_types and obj.get("puppet_rig"):
            rig_name = obj["puppet_rig"]
            if rig_name in bpy.data.objects:
                return bpy.data.objects[rig_name]

    # Fallback: search all objects for any puppet armature
    for o in bpy.data.objects:
        if o.type == 'ARMATURE' and o.get("is_puppet"):
            return o

    return None


# ----------------------------------------------------------------------------
# VIEW THIS VIEW - Show ALL drawn parts for current view
# ----------------------------------------------------------------------------

class PUPPET_OT_view_part(Operator):
    """Show all drawn parts as an assembled character"""

    bl_idname = "puppet.view_part"
    bl_label = "View Puppet"
    bl_description = "Show all drawn parts (assembled character view)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return get_puppet_armature(context) is not None

    def execute(self, context):
        """Show drawn GP objects for the current view at full opacity."""
        armature = get_puppet_armature(context)
        if not armature:
            self.report({'ERROR'}, "No puppet found")
            return {'CANCELLED'}

        # Exit any current mode
        if context.active_object and context.active_object.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass

        # Get layers relevant to current view + hand pose
        relevant_layers = get_view_layer_names(context)

        # Show/hide GP objects based on current view
        from ..core.rig_builder import get_puppet_gp_objects
        all_gps = get_puppet_gp_objects(armature)
        shown = 0

        for gp_obj, gp_layer in all_gps:
            if gp_layer in relevant_layers:
                gp_obj.hide_viewport = False
                gp_obj.hide_render = False
                if gp_obj.data.layers:
                    gp_obj.data.layers[0].opacity = 1.0
                shown += 1
            else:
                gp_obj.hide_viewport = True

        # Select armature
        for obj in bpy.data.objects:
            obj.select_set(False)
        armature.select_set(True)
        context.view_layer.objects.active = armature

        self.report({'INFO'}, f"Viewing {shown} drawn parts")
        return {'FINISHED'}


# ----------------------------------------------------------------------------
# DRAW THIS VIEW - Create/select GP object and enter draw mode
# Other drawn parts stay visible as reference (separate GP objects)
# ----------------------------------------------------------------------------

class PUPPET_OT_draw_part(Operator):
    """Activate the selected body part and enter Grease Pencil Draw mode"""

    bl_idname = "puppet.draw_part"
    bl_label = "Draw This View"
    bl_description = "Activate this part and start drawing (other parts visible as reference)"
    bl_options = {'REGISTER', 'UNDO'}

    layer_name: StringProperty(
        name="Layer Name",
        description="Specific layer to activate (optional)",
        default="",
    )

    @classmethod
    def poll(cls, context):
        return get_puppet_armature(context) is not None

    def execute(self, context):
        """Find or create the GP object for this part and enter draw mode."""
        armature = get_puppet_armature(context)
        if not armature:
            self.report({'ERROR'}, "No puppet found")
            return {'CANCELLED'}

        # Determine target layer
        if self.layer_name:
            layer_name = self.layer_name
        else:
            layer_name = get_current_layer_name(context)

        props = context.scene.puppet_selector
        ref_opacity = getattr(props, 'reference_opacity', 0.3)

        # Get/create the GP object for this part (on-demand creation)
        from ..core.rig_builder import find_or_create_gp_for_layer, get_puppet_gp_objects
        target_gp = find_or_create_gp_for_layer(armature, layer_name, context)

        # Get layers relevant to current view
        relevant_layers = get_view_layer_names(context)

        # Set visibility for all puppet GP objects
        all_gps = get_puppet_gp_objects(armature)
        for gp_obj, gp_layer in all_gps:
            if gp_obj == target_gp:
                # Target: full opacity, visible
                gp_obj.hide_viewport = False
                if gp_obj.data.layers:
                    gp_obj.data.layers[0].opacity = 1.0
            elif gp_layer in relevant_layers:
                # Same view, different part: show as reference
                gp_obj.hide_viewport = False
                if gp_obj.data.layers:
                    gp_obj.data.layers[0].opacity = ref_opacity
            else:
                # Different view: hide
                gp_obj.hide_viewport = True

        # Exit any current mode
        if context.active_object and context.active_object.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass

        # Select the target GP object
        for obj in bpy.data.objects:
            obj.select_set(False)
        target_gp.select_set(True)
        context.view_layer.objects.active = target_gp

        # Enter paint mode
        try:
            bpy.ops.object.mode_set(mode='PAINT_GREASE_PENCIL')
        except TypeError:
            try:
                bpy.ops.object.mode_set(mode='PAINT_GPENCIL')
            except Exception as e:
                print(f"Puppet Mode: Could not enter draw mode: {e}")

        self.report({'INFO'}, f"Drawing: {layer_name}")
        return {'FINISHED'}


# ----------------------------------------------------------------------------
# SET ROTATION - Select rotation from grid
# ----------------------------------------------------------------------------

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

    # Option to also view the layer immediately
    auto_view: BoolProperty(
        name="Auto View",
        description="Automatically show the selected view",
        default=True,
    )

    def execute(self, context):
        """Set the rotation property and optionally view it."""
        props = context.scene.puppet_selector
        props.rotation = self.rotation

        # Auto-view when clicking on rotation grid
        if self.auto_view:
            bpy.ops.puppet.view_part()

        return {'FINISHED'}


# ----------------------------------------------------------------------------
# TOGGLE ONION SKIN - Show/hide other rotation views faintly
# ----------------------------------------------------------------------------

class PUPPET_OT_toggle_onion(Operator):
    """Toggle onion skin visibility for other rotation views"""

    bl_idname = "puppet.toggle_onion"
    bl_label = "Toggle Onion Skin"
    bl_description = "Show/hide other rotation views as faint guides"
    bl_options = {'REGISTER'}

    def execute(self, context):
        """Toggle onion skin setting."""
        props = context.scene.puppet_selector

        # Toggle the setting
        props.onion_skin_enabled = not props.onion_skin_enabled

        # Refresh the view if a puppet is active
        if get_puppet_armature(context):
            bpy.ops.puppet.view_part()

        status = "ON" if props.onion_skin_enabled else "OFF"
        self.report({'INFO'}, f"Onion skin: {status}")
        return {'FINISHED'}


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

classes = [
    PUPPET_OT_view_part,
    PUPPET_OT_draw_part,
    PUPPET_OT_set_rotation,
    PUPPET_OT_toggle_onion,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
