# panels/main_panel.py
# ============================================================================
# Main UI panel for Puppet Mode.
# This appears in the 3D View sidebar (N-panel) under "Puppet Mode" tab.
# Phase 1c: Full body part selector with rotation views.
# ============================================================================

import bpy
from bpy.types import Panel, Operator

from ..core.rig_builder import get_puppets_in_scene
from ..core.properties import (
    get_current_layer_name,
    is_layer_drawn,
    count_drawn_layers,
)
from ..constants import (
    get_total_drawable_parts,
    ROTATION_VIEWS_FULL,
    ROTATION_VIEWS_SIMPLE,
    HAND_ROTATION_VIEWS,
    HAND_POSES,
)


class PUPPET_PT_main_panel(Panel):
    """Main Puppet Mode panel in the 3D View sidebar"""

    bl_label = "Puppet Mode"
    bl_idname = "PUPPET_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Puppet Mode"

    def draw(self, context):
        layout = self.layout
        props = context.scene.puppet_selector

        # Get active puppet
        active_puppet, gp_obj = self._get_active_puppet(context)

        # --------------------------------------------------------------------
        # NO PUPPET SELECTED
        # --------------------------------------------------------------------
        if active_puppet is None:
            self._draw_no_puppet(layout, context)
            return

        # --------------------------------------------------------------------
        # PUPPET HEADER
        # --------------------------------------------------------------------
        self._draw_puppet_header(layout, active_puppet, gp_obj)

        # --------------------------------------------------------------------
        # BODY PART SELECTOR
        # --------------------------------------------------------------------
        self._draw_body_selector(layout, context, props, gp_obj)

    def _get_active_puppet(self, context):
        """Find the active puppet armature and its GP object."""
        obj = context.active_object
        active_puppet = None
        gp_obj = None

        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            active_puppet = obj
            gp_name = obj.get("puppet_gp")
            if gp_name and gp_name in bpy.data.objects:
                gp_obj = bpy.data.objects[gp_name]

        elif obj and obj.type == 'GPENCIL' and obj.get("puppet_rig"):
            gp_obj = obj
            rig_name = obj.get("puppet_rig")
            if rig_name and rig_name in bpy.data.objects:
                active_puppet = bpy.data.objects[rig_name]

        return active_puppet, gp_obj

    def _draw_no_puppet(self, layout, context):
        """Draw UI when no puppet is selected."""
        box = layout.box()
        box.label(text="No puppet selected", icon='INFO')

        # List existing puppets
        puppets = get_puppets_in_scene()
        if puppets:
            box.label(text="Select a puppet:")
            for puppet in puppets:
                row = box.row(align=True)
                row.label(text=puppet["puppet_name"], icon='ARMATURE_DATA')
                op = row.operator("puppet.select_puppet", text="", icon='RESTRICT_SELECT_OFF')
                op.puppet_name = puppet.name

        # Create new puppet button
        layout.separator()
        layout.operator("puppet.create_puppet", text="Create New Puppet", icon='ADD')

    def _draw_puppet_header(self, layout, puppet, gp_obj):
        """Draw puppet name and progress."""
        box = layout.box()

        # Puppet name
        row = box.row()
        row.label(text=puppet["puppet_name"], icon='ARMATURE_DATA')

        # Progress indicator
        if gp_obj:
            drawn, total = count_drawn_layers(gp_obj)
            progress = drawn / total if total > 0 else 0

            row = box.row()
            row.label(text=f"Parts Drawn: {drawn}/{total}")

            # Progress bar
            row = box.row()
            row.progress(factor=progress, type='BAR', text=f"{int(progress * 100)}%")

    def _draw_body_selector(self, layout, context, props, gp_obj):
        """Draw the body part and rotation selector."""

        # --------------------------------------------------------------------
        # BODY REGION SELECTOR (Face / Body / Hands)
        # --------------------------------------------------------------------
        box = layout.box()
        box.label(text="Body Region", icon='OUTLINER_OB_ARMATURE')

        row = box.row(align=True)
        row.prop(props, "region", expand=True)

        # --------------------------------------------------------------------
        # PART SELECTOR (dropdown)
        # --------------------------------------------------------------------
        box = layout.box()
        box.label(text="Select Part", icon='BONE_DATA')
        box.prop(props, "part", text="")

        # --------------------------------------------------------------------
        # HAND POSE SELECTOR (only for hands)
        # --------------------------------------------------------------------
        if props.region == 'HANDS':
            box = layout.box()
            box.label(text="Hand Pose", icon='VIEW_PAN')
            row = box.row(align=True)
            row.prop(props, "hand_pose", expand=True)

        # --------------------------------------------------------------------
        # ROTATION VIEW SELECTOR
        # --------------------------------------------------------------------
        part = props.part

        # Skip rotation for shape-key parts
        if part not in ['Eyes', 'Eyebrows', 'Mouth']:
            box = layout.box()
            box.label(text="Rotation View", icon='ORIENTATION_VIEW')

            # Determine rotation type
            if part in ['Head', 'Chest', 'Spine', 'Hips']:
                self._draw_rotation_grid_full(box, context, props, gp_obj)
            elif part.startswith('Hand_'):
                self._draw_rotation_grid_hand(box, context, props, gp_obj)
            else:
                self._draw_rotation_grid_simple(box, context, props, gp_obj)

        # --------------------------------------------------------------------
        # CURRENT SELECTION STATUS
        # --------------------------------------------------------------------
        box = layout.box()
        layer_name = get_current_layer_name(context)
        is_drawn = is_layer_drawn(gp_obj, layer_name) if gp_obj else False

        row = box.row()
        if is_drawn:
            row.label(text=f"{layer_name}", icon='CHECKMARK')
            row.label(text="drawn")
        else:
            row.label(text=f"{layer_name}", icon='LAYER_ACTIVE')
            row.label(text="not drawn")

        # --------------------------------------------------------------------
        # ONION SKIN CONTROLS
        # --------------------------------------------------------------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(props, "onion_skin_enabled", text="Onion Skin", toggle=True)
        if props.onion_skin_enabled:
            row.prop(props, "onion_skin_opacity", text="", slider=True)

        # --------------------------------------------------------------------
        # VIEW / DRAW BUTTONS
        # --------------------------------------------------------------------
        layout.separator()

        # View button (see what you drew)
        row = layout.row()
        row.scale_y = 1.5
        row.operator("puppet.view_part", text="VIEW", icon='HIDE_OFF')

        # Draw button
        row = layout.row()
        row.scale_y = 2.0
        row.operator("puppet.draw_part", text="DRAW", icon='GREASEPENCIL')

    def _draw_rotation_grid_full(self, box, context, props, gp_obj):
        """
        Draw the 6-direction rotation selector:
              [3Q_L] [Front] [3Q_R]
        [Side_L]    [●]    [Side_R]
                  [Back]
        """
        part = props.part
        current = props.rotation

        # Row 1: 3Q_L, Front, 3Q_R
        row = box.row(align=True)
        self._rotation_button(row, "3Q_L", part, current, gp_obj)
        self._rotation_button(row, "Front", part, current, gp_obj)
        self._rotation_button(row, "3Q_R", part, current, gp_obj)

        # Row 2: Side_L, (center), Side_R
        row = box.row(align=True)
        self._rotation_button(row, "Side_L", part, current, gp_obj)
        row.label(text="", icon='RADIOBUT_ON' if current else 'RADIOBUT_OFF')
        self._rotation_button(row, "Side_R", part, current, gp_obj)

        # Row 3: Back
        row = box.row(align=True)
        row.label(text="")
        self._rotation_button(row, "Back", part, current, gp_obj)
        row.label(text="")

    def _draw_rotation_grid_simple(self, box, context, props, gp_obj):
        """Draw simple Front/Side selector for arms/legs."""
        part = props.part
        current = props.rotation

        row = box.row(align=True)
        self._rotation_button(row, "Front", part, current, gp_obj)
        self._rotation_button(row, "Side", part, current, gp_obj)

    def _draw_rotation_grid_hand(self, box, context, props, gp_obj):
        """Draw Front/Back selector for hands."""
        part = props.part
        current = props.rotation

        row = box.row(align=True)
        self._rotation_button(row, "Front", part, current, gp_obj, hand_pose=props.hand_pose)
        self._rotation_button(row, "Back", part, current, gp_obj, hand_pose=props.hand_pose)

    def _rotation_button(self, row, rotation, part, current, gp_obj, hand_pose=None):
        """
        Draw a single rotation button.
        Shows different icons based on:
        - Current selection (highlighted)
        - Whether the layer has been drawn (filled vs empty)
        """
        # Determine layer name for this rotation
        if hand_pose:
            layer_name = f"{part}_{hand_pose}_{rotation}"
        else:
            layer_name = f"{part}_{rotation}"

        # Check if drawn
        is_drawn = is_layer_drawn(gp_obj, layer_name) if gp_obj else False
        is_current = (rotation == current)

        # Choose icon
        if is_current:
            icon = 'RADIOBUT_ON'
        elif is_drawn:
            icon = 'CHECKBOX_HLT'
        else:
            icon = 'CHECKBOX_DEHLT'

        # Draw button
        op = row.operator("puppet.set_rotation", text=rotation.replace('_', ' '), icon=icon, depress=is_current)
        op.rotation = rotation


# ----------------------------------------------------------------------------
# HELPER OPERATOR: Select Puppet
# ----------------------------------------------------------------------------

class PUPPET_OT_select_puppet(Operator):
    """Select a puppet by name"""

    bl_idname = "puppet.select_puppet"
    bl_label = "Select Puppet"
    bl_options = {'REGISTER', 'UNDO'}

    puppet_name: bpy.props.StringProperty(name="Puppet Name")

    def execute(self, context):
        if self.puppet_name in bpy.data.objects:
            puppet = bpy.data.objects[self.puppet_name]
            for obj in bpy.data.objects:
                obj.select_set(False)
            puppet.select_set(True)
            context.view_layer.objects.active = puppet
            self.report({'INFO'}, f"Selected {self.puppet_name}")
        return {'FINISHED'}


class PUPPET_OT_select_gp(Operator):
    """Select the Grease Pencil object for the active puppet"""

    bl_idname = "puppet.select_gp"
    bl_label = "Select GP Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            gp_name = obj.get("puppet_gp")
            if gp_name and gp_name in bpy.data.objects:
                gp_obj = bpy.data.objects[gp_name]
                for o in bpy.data.objects:
                    o.select_set(False)
                gp_obj.select_set(True)
                context.view_layer.objects.active = gp_obj
                self.report({'INFO'}, f"Selected {gp_name}")
                return {'FINISHED'}

        self.report({'WARNING'}, "No puppet GP object found")
        return {'CANCELLED'}


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

classes = [
    PUPPET_PT_main_panel,
    PUPPET_OT_select_puppet,
    PUPPET_OT_select_gp,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
