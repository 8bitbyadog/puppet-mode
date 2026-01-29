# panels/main_panel.py
# ============================================================================
# Main UI panel for Puppet Mode.
# This appears in the 3D View sidebar (N-panel) under "Puppet Mode" tab.
#
# PER-OBJECT ARCHITECTURE: Each body part has its own GP object.
# - Puppet armature is the root; GP objects are children
# - "Drawn" means the GP object exists (created on-demand)
# - Visibility toggles use hide_viewport on GP objects
# ============================================================================

import bpy
from bpy.types import Panel, Operator

from ..core.rig_builder import get_puppets_in_scene
from ..core.properties import (
    get_current_layer_name,
    is_layer_drawn,
    count_drawn_parts,
)
from ..constants import (
    get_total_drawable_parts,
    get_gp_object_name,
    CHARACTER_VIEWS,
    DRAWABLE_PARTS,
    VIEW_DEPENDENT_PARTS,
    OUTLINER_PARTS,
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

        # Get active puppet armature
        active_puppet = self._get_active_puppet(context)

        # --------------------------------------------------------------------
        # NO PUPPET SELECTED
        # --------------------------------------------------------------------
        if active_puppet is None:
            self._draw_no_puppet(layout, context)
            return

        # --------------------------------------------------------------------
        # PUPPET HEADER
        # --------------------------------------------------------------------
        self._draw_puppet_header(layout, active_puppet)

        # --------------------------------------------------------------------
        # CHARACTER VIEW SELECTOR (Primary)
        # --------------------------------------------------------------------
        self._draw_view_selector(layout, context, props, active_puppet)

        # --------------------------------------------------------------------
        # PART SELECTOR (Simplified)
        # --------------------------------------------------------------------
        self._draw_part_selector(layout, context, props)

        # --------------------------------------------------------------------
        # CURRENT SELECTION & ACTIONS
        # --------------------------------------------------------------------
        self._draw_action_buttons(layout, context, props, active_puppet)

        # --------------------------------------------------------------------
        # MINI-OUTLINER (Visibility Controls)
        # --------------------------------------------------------------------
        self._draw_mini_outliner(layout, context, props, active_puppet)

    def _get_active_puppet(self, context):
        """Find the active puppet armature."""
        obj = context.active_object
        gp_types = ('GPENCIL', 'GREASEPENCIL')

        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            return obj

        if obj and obj.type in gp_types and obj.get("puppet_rig"):
            rig_name = obj.get("puppet_rig")
            if rig_name and rig_name in bpy.data.objects:
                return bpy.data.objects[rig_name]

        return None

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

    def _draw_puppet_header(self, layout, puppet):
        """Draw puppet name and progress."""
        box = layout.box()

        # Puppet name
        row = box.row()
        row.label(text=puppet["puppet_name"], icon='ARMATURE_DATA')

        # Progress indicator
        drawn, total = count_drawn_parts(puppet)
        progress = drawn / total if total > 0 else 0

        row = box.row()
        row.label(text=f"Parts Drawn: {drawn}/{total}")

        # Progress bar
        row = box.row()
        row.progress(factor=progress, type='BAR', text=f"{int(progress * 100)}%")

    def _draw_view_selector(self, layout, context, props, puppet):
        """Draw the character view selector (Front, Quarter, Profile)."""
        box = layout.box()
        box.label(text="Character View", icon='ORIENTATION_VIEW')

        # View buttons in a row
        row = box.row(align=True)
        for view in CHARACTER_VIEWS:
            # Check if any parts are drawn for this view
            view_has_content = self._view_has_content(puppet, view)

            # Nicer labels
            label = view.replace('_', ' ')
            if view == 'Quarter_L':
                label = "3/4 L"
            elif view == 'Quarter_R':
                label = "3/4 R"
            elif view == 'Profile_L':
                label = "Side L"
            elif view == 'Profile_R':
                label = "Side R"

            # Icon shows if view has content
            is_current = (props.character_view == view)
            if is_current:
                icon = 'RADIOBUT_ON'
            elif view_has_content:
                icon = 'CHECKBOX_HLT'
            else:
                icon = 'CHECKBOX_DEHLT'

            op = row.operator("puppet.set_view", text=label, icon=icon, depress=is_current)
            op.view = view

    def _draw_part_selector(self, layout, context, props):
        """Draw simplified part selector."""
        box = layout.box()
        box.label(text="Select Part to Draw", icon='BONE_DATA')

        # Region filter (optional, collapsed by default)
        row = box.row(align=True)
        row.prop(props, "region", expand=True)

        # Part dropdown
        box.prop(props, "part", text="")

        # Hand pose selector (only for hands)
        if props.part.startswith('Hand_'):
            row = box.row(align=True)
            row.label(text="Pose:")
            for pose in HAND_POSES:
                is_current = (props.hand_pose == pose)
                icon = 'RADIOBUT_ON' if is_current else 'RADIOBUT_OFF'
                op = row.operator("puppet.set_hand_pose", text=pose, icon=icon, depress=is_current)
                op.pose = pose

    def _draw_action_buttons(self, layout, context, props, puppet):
        """Draw current selection status and action buttons."""
        box = layout.box()

        # Current selection
        layer_name = get_current_layer_name(context)
        is_drawn = is_layer_drawn(puppet, layer_name)

        row = box.row()
        if is_drawn:
            row.label(text=f"{layer_name}", icon='CHECKMARK')
        else:
            row.label(text=f"{layer_name}", icon='LAYER_ACTIVE')

        # Reference opacity while drawing
        row = box.row(align=True)
        row.label(text="Ref Opacity:")
        row.prop(props, "reference_opacity", text="", slider=True)

        # Action buttons
        layout.separator()

        # View button (show assembled character)
        row = layout.row()
        row.scale_y = 1.5
        row.operator("puppet.view_part", text="VIEW ALL", icon='HIDE_OFF')

        # Draw button
        row = layout.row()
        row.scale_y = 2.0
        op_text = "DRAW" if not is_drawn else "EDIT"
        row.operator("puppet.draw_part", text=op_text, icon='GREASEPENCIL')

    def _draw_mini_outliner(self, layout, context, props, puppet):
        """Draw mini-outliner with visibility toggles for each part."""
        box = layout.box()

        # Collapsible header
        row = box.row()
        row.label(text="Parts (Outliner)", icon='OUTLINER')

        if not puppet:
            return

        current_view = props.character_view
        puppet_name = puppet.get("puppet_name", "")

        # List each part with visibility toggle and drawn status
        for part_id, part_label in OUTLINER_PARTS:
            row = box.row(align=True)

            # Determine the layer name for this part
            if part_id in VIEW_DEPENDENT_PARTS:
                layer_name = f"{part_id}_{current_view}"
            elif part_id.startswith('Hand_'):
                layer_name = f"{part_id}_{props.hand_pose}"
            else:
                layer_name = part_id

            # Check if drawn (GP object exists)
            drawn = is_layer_drawn(puppet, layer_name)

            # Visibility toggle (only if GP object exists)
            if drawn:
                gp_name = get_gp_object_name(puppet_name, layer_name)
                gp_obj = bpy.data.objects.get(gp_name)
                if gp_obj:
                    icon_vis = 'HIDE_OFF' if not gp_obj.hide_viewport else 'HIDE_ON'
                    op = row.operator("puppet.toggle_layer_visibility", text="", icon=icon_vis)
                    op.layer_name = layer_name
                else:
                    row.label(text="", icon='BLANK1')
            else:
                row.label(text="", icon='BLANK1')

            # Part label with drawn indicator
            icon = 'CHECKMARK' if drawn else 'DOT'
            row.label(text=part_label, icon=icon)

            # Select button
            is_selected = (props.part == part_id)
            icon_sel = 'LAYER_ACTIVE' if is_selected else 'LAYER_USED'
            op = row.operator("puppet.quick_select_part", text="", icon=icon_sel)
            op.part = part_id

    def _view_has_content(self, puppet, view):
        """Check if any parts have been drawn for a given view."""
        if not puppet:
            return False

        for part in VIEW_DEPENDENT_PARTS:
            layer_name = f"{part}_{view}"
            if is_layer_drawn(puppet, layer_name):
                return True
        return False


# ----------------------------------------------------------------------------
# HELPER OPERATORS
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


class PUPPET_OT_set_view(Operator):
    """Set the character view angle"""

    bl_idname = "puppet.set_view"
    bl_label = "Set View"
    bl_options = {'REGISTER'}

    view: bpy.props.StringProperty(name="View", default="Front")

    def execute(self, context):
        props = context.scene.puppet_selector
        props.character_view = self.view
        # Refresh the view to show parts for this angle
        bpy.ops.puppet.view_part()
        return {'FINISHED'}


class PUPPET_OT_set_hand_pose(Operator):
    """Set the hand pose"""

    bl_idname = "puppet.set_hand_pose"
    bl_label = "Set Hand Pose"
    bl_options = {'REGISTER'}

    pose: bpy.props.StringProperty(name="Pose", default="Open")

    def execute(self, context):
        props = context.scene.puppet_selector
        props.hand_pose = self.pose
        return {'FINISHED'}


class PUPPET_OT_toggle_layer_visibility(Operator):
    """Toggle visibility of a specific part's GP object"""

    bl_idname = "puppet.toggle_layer_visibility"
    bl_label = "Toggle Layer Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    layer_name: bpy.props.StringProperty(name="Layer Name")

    def execute(self, context):
        # Find puppet armature
        obj = context.active_object
        armature = None
        gp_types = ('GPENCIL', 'GREASEPENCIL')

        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            armature = obj
        elif obj and obj.type in gp_types and obj.get("puppet_rig"):
            rig_name = obj["puppet_rig"]
            if rig_name in bpy.data.objects:
                armature = bpy.data.objects[rig_name]

        if not armature:
            self.report({'WARNING'}, "No puppet found")
            return {'CANCELLED'}

        puppet_name = armature.get("puppet_name", "")
        gp_name = get_gp_object_name(puppet_name, self.layer_name)
        gp_obj = bpy.data.objects.get(gp_name)

        if gp_obj:
            gp_obj.hide_viewport = not gp_obj.hide_viewport
            status = "hidden" if gp_obj.hide_viewport else "visible"
            self.report({'INFO'}, f"{self.layer_name}: {status}")
        else:
            self.report({'WARNING'}, f"No drawing found for {self.layer_name}")

        return {'FINISHED'}


class PUPPET_OT_quick_select_part(Operator):
    """Quickly select a part from the outliner"""

    bl_idname = "puppet.quick_select_part"
    bl_label = "Select Part"
    bl_options = {'REGISTER'}

    part: bpy.props.StringProperty(name="Part")

    def execute(self, context):
        props = context.scene.puppet_selector

        # Set the region based on part
        if self.part in ['Head', 'Face_Features', 'Mouth']:
            props.region = 'FACE'
        elif self.part.startswith('Hand_'):
            props.region = 'HANDS'
        else:
            props.region = 'BODY'

        # Set the part (needs to happen after region for enum to be valid)
        props.part = self.part

        return {'FINISHED'}


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

classes = [
    PUPPET_PT_main_panel,
    PUPPET_OT_select_puppet,
    PUPPET_OT_set_view,
    PUPPET_OT_set_hand_pose,
    PUPPET_OT_toggle_layer_visibility,
    PUPPET_OT_quick_select_part,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
