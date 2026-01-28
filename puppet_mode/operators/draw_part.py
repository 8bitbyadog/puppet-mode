# operators/draw_part.py
# ============================================================================
# Operators for viewing and drawing on specific body part layers.
# Includes: Draw This View, View This View, Set Rotation, Onion Skin Toggle
# ============================================================================

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, FloatProperty

from ..core.properties import get_current_layer_name
from ..constants import (
    ROTATION_VIEWS_FULL,
    ROTATION_VIEWS_SIMPLE,
    HAND_ROTATION_VIEWS,
    HAND_POSES,
    GP_LAYER_STRUCTURE,
)


def get_gp_object_type():
    """
    Get the correct GP object type string for this Blender version.
    Blender 5.0+ uses 'GREASEPENCIL', older versions use 'GPENCIL'.
    """
    if bpy.app.version >= (5, 0, 0):
        return 'GREASEPENCIL'
    return 'GPENCIL'


def get_gp_object_from_context(context):
    """Find the GP object for the active puppet."""
    obj = context.active_object
    gp_type = get_gp_object_type()

    # If GP object is selected, use it
    if obj and obj.type in (gp_type, 'GPENCIL') and obj.get("puppet_rig"):
        return obj

    # If armature is selected, find its GP object
    if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
        gp_name = obj.get("puppet_gp")
        if gp_name and gp_name in bpy.data.objects:
            return bpy.data.objects[gp_name]

    # Search all objects for a puppet GP
    for o in bpy.data.objects:
        if o.type in (gp_type, 'GPENCIL') and o.get("puppet_rig"):
            return o

    return None


def get_related_rotation_layers(part, current_rotation, hand_pose=None):
    """
    Get list of layer names for other rotation views of the same part.
    Used for onion skinning.
    """
    related = []

    # Determine which rotation set this part uses
    if part in ['Head', 'Chest', 'Spine', 'Hips']:
        rotations = ROTATION_VIEWS_FULL
    elif part.startswith('Hand_'):
        rotations = HAND_ROTATION_VIEWS
    elif part.startswith(('Arm_', 'Leg_', 'Foot_')):
        rotations = ROTATION_VIEWS_SIMPLE
    else:
        return []

    for rot in rotations:
        if rot != current_rotation:
            if hand_pose and part.startswith('Hand_'):
                related.append(f"{part}_{hand_pose}_{rot}")
            else:
                related.append(f"{part}_{rot}")

    return related


# ----------------------------------------------------------------------------
# VIEW THIS VIEW - Show layer without entering draw mode
# ----------------------------------------------------------------------------

class PUPPET_OT_view_part(Operator):
    """Show the selected body part layer (view mode, not draw mode)"""

    bl_idname = "puppet.view_part"
    bl_label = "View This View"
    bl_description = "Show this layer without entering draw mode"
    bl_options = {'REGISTER', 'UNDO'}

    layer_name: StringProperty(
        name="Layer Name",
        description="Specific layer to view (optional)",
        default="",
    )

    @classmethod
    def poll(cls, context):
        """Check if we can execute (need an active puppet)."""
        return get_gp_object_from_context(context) is not None

    def execute(self, context):
        """Show the layer in object mode."""
        gp_obj = get_gp_object_from_context(context)
        if not gp_obj:
            self.report({'ERROR'}, "No puppet GP object found")
            return {'CANCELLED'}

        # Determine which layer to show
        if self.layer_name:
            layer_name = self.layer_name
        else:
            layer_name = get_current_layer_name(context)

        gp_data = gp_obj.data
        layer = gp_data.layers.get(layer_name)

        if not layer:
            self.report({'WARNING'}, f"Layer '{layer_name}' not found")
            return {'CANCELLED'}

        # Exit any current mode
        if context.active_object and context.active_object.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass

        # Select the GP object
        for obj in bpy.data.objects:
            obj.select_set(False)
        gp_obj.select_set(True)
        context.view_layer.objects.active = gp_obj

        # Check if onion skin is enabled
        props = context.scene.puppet_selector
        onion_enabled = getattr(props, 'onion_skin_enabled', False)
        onion_opacity = getattr(props, 'onion_skin_opacity', 0.2)

        # Get related layers for onion skin
        part = props.part
        rotation = props.rotation
        hand_pose = props.hand_pose if props.region == 'HANDS' else None
        related_layers = get_related_rotation_layers(part, rotation, hand_pose)

        # Set layer visibility
        for lyr in gp_data.layers:
            if lyr.name == layer_name:
                # Target layer: fully visible
                lyr.hide = False
                lyr.opacity = 1.0
            elif onion_enabled and lyr.name in related_layers:
                # Onion skin layer: visible but faint
                lyr.hide = False
                lyr.opacity = onion_opacity
            else:
                # Other layers: hidden
                lyr.hide = True

        # Make target layer active
        gp_data.layers.active = layer

        self.report({'INFO'}, f"Viewing: {layer_name}")
        return {'FINISHED'}


# ----------------------------------------------------------------------------
# DRAW THIS VIEW - Activate layer and enter draw mode
# ----------------------------------------------------------------------------

class PUPPET_OT_draw_part(Operator):
    """Activate the selected body part layer and enter Grease Pencil Draw mode"""

    bl_idname = "puppet.draw_part"
    bl_label = "Draw This View"
    bl_description = "Activate this layer and start drawing"
    bl_options = {'REGISTER', 'UNDO'}

    layer_name: StringProperty(
        name="Layer Name",
        description="Specific layer to activate (optional)",
        default="",
    )

    @classmethod
    def poll(cls, context):
        """Check if we can execute (need an active puppet)."""
        return get_gp_object_from_context(context) is not None

    def execute(self, context):
        """Activate the layer and enter draw mode."""
        gp_obj = get_gp_object_from_context(context)
        if not gp_obj:
            self.report({'ERROR'}, "No puppet GP object found")
            return {'CANCELLED'}

        # Determine which layer to activate
        if self.layer_name:
            layer_name = self.layer_name
        else:
            layer_name = get_current_layer_name(context)

        gp_data = gp_obj.data
        layer = gp_data.layers.get(layer_name)

        if not layer:
            self.report({'WARNING'}, f"Layer '{layer_name}' not found")
            return {'CANCELLED'}

        # Exit any current mode first
        if context.active_object and context.active_object.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass

        # Select the GP object
        for obj in bpy.data.objects:
            obj.select_set(False)
        gp_obj.select_set(True)
        context.view_layer.objects.active = gp_obj

        # Check if onion skin is enabled
        props = context.scene.puppet_selector
        onion_enabled = getattr(props, 'onion_skin_enabled', False)
        onion_opacity = getattr(props, 'onion_skin_opacity', 0.2)

        # Get related layers for onion skin
        part = props.part
        rotation = props.rotation
        hand_pose = props.hand_pose if props.region == 'HANDS' else None
        related_layers = get_related_rotation_layers(part, rotation, hand_pose)

        # Set layer visibility
        for lyr in gp_data.layers:
            if lyr.name == layer_name:
                # Target layer: fully visible, unlocked
                lyr.hide = False
                lyr.opacity = 1.0
                lyr.lock = False
            elif onion_enabled and lyr.name in related_layers:
                # Onion skin layer: visible but faint and locked
                lyr.hide = False
                lyr.opacity = onion_opacity
                lyr.lock = True  # Prevent drawing on wrong layer
            else:
                # Other layers: hidden
                lyr.hide = True

        # Make target layer active
        gp_data.layers.active = layer

        # Enter Draw mode
        self._enter_draw_mode(context)

        self.report({'INFO'}, f"Drawing on: {layer_name}")
        return {'FINISHED'}

    def _enter_draw_mode(self, context):
        """Enter GP draw mode, handling version differences."""
        try:
            bpy.ops.object.mode_set(mode='PAINT_GREASE_PENCIL')
        except TypeError:
            try:
                bpy.ops.object.mode_set(mode='PAINT_GPENCIL')
            except Exception as e:
                print(f"Puppet Mode: Could not enter draw mode: {e}")


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

        # Refresh the view if a puppet is selected
        gp_obj = get_gp_object_from_context(context)
        if gp_obj:
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
