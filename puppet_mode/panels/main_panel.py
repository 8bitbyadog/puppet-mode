# panels/main_panel.py
# ============================================================================
# Main UI panel for Puppet Mode.
# This appears in the 3D View sidebar (N-panel) under "Puppet Mode" tab.
# ============================================================================

import bpy
from bpy.types import Panel

from ..core.rig_builder import get_puppets_in_scene
from ..constants import get_total_drawable_parts


class PUPPET_PT_main_panel(Panel):
    """Main Puppet Mode panel in the 3D View sidebar"""

    bl_label = "Puppet Mode"
    bl_idname = "PUPPET_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Puppet Mode"  # Tab name in the N-panel

    def draw(self, context):
        layout = self.layout

        # Get active object to check if it's a puppet
        obj = context.active_object
        active_puppet = None

        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            active_puppet = obj
        elif obj and obj.type == 'GPENCIL' and obj.get("puppet_rig"):
            # If GP object selected, find its rig
            rig_name = obj.get("puppet_rig")
            if rig_name and rig_name in bpy.data.objects:
                active_puppet = bpy.data.objects[rig_name]

        # --------------------------------------------------------------------
        # CREATE SECTION (shown when no puppet is selected)
        # --------------------------------------------------------------------
        if active_puppet is None:
            box = layout.box()
            box.label(text="No puppet selected", icon='INFO')

            # List existing puppets
            puppets = get_puppets_in_scene()
            if puppets:
                box.label(text="Puppets in scene:")
                for puppet in puppets:
                    row = box.row()
                    row.label(text=puppet["puppet_name"], icon='ARMATURE_DATA')
                    # Select button
                    op = row.operator(
                        "object.select_all",
                        text="",
                        icon='RESTRICT_SELECT_OFF'
                    )

            # Create new puppet button
            layout.separator()
            layout.operator(
                "puppet.create_puppet",
                text="Create New Puppet",
                icon='ADD'
            )

        # --------------------------------------------------------------------
        # PUPPET INFO SECTION (shown when puppet is selected)
        # --------------------------------------------------------------------
        else:
            # Header with puppet name
            box = layout.box()
            row = box.row()
            row.label(text=active_puppet["puppet_name"], icon='ARMATURE_DATA')

            # Progress indicator (placeholder for Phase 1c)
            total_parts = get_total_drawable_parts()
            drawn_parts = 0  # Will be calculated in Phase 1c

            row = box.row()
            row.label(text=f"Parts Drawn: {drawn_parts}/{total_parts}")

            # Progress bar (visual representation)
            progress = drawn_parts / total_parts if total_parts > 0 else 0
            row = box.row()
            row.progress(
                factor=progress,
                type='BAR',
                text=f"{int(progress * 100)}%"
            )

            # ------------------------------------------------------------
            # BODY PART SELECTOR (placeholder for Phase 1c)
            # ------------------------------------------------------------
            layout.separator()
            box = layout.box()
            box.label(text="Body Part Selector", icon='BONE_DATA')
            box.label(text="(Coming in Phase 1c)", icon='TIME')

            # ------------------------------------------------------------
            # QUICK ACTIONS
            # ------------------------------------------------------------
            layout.separator()
            box = layout.box()
            box.label(text="Quick Actions", icon='TOOL_SETTINGS')

            # Button to select the GP object
            gp_name = active_puppet.get("puppet_gp")
            if gp_name and gp_name in bpy.data.objects:
                row = box.row()
                row.operator(
                    "puppet.select_gp",
                    text="Select Drawing Object",
                    icon='GREASEPENCIL'
                )

            # Create another puppet
            row = box.row()
            row.operator(
                "puppet.create_puppet",
                text="Create Another Puppet",
                icon='ADD'
            )


# ----------------------------------------------------------------------------
# HELPER OPERATOR: Select GP Object
# ----------------------------------------------------------------------------

class PUPPET_OT_select_gp(bpy.types.Operator):
    """Select the Grease Pencil object for the active puppet"""

    bl_idname = "puppet.select_gp"
    bl_label = "Select GP Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        # Find the puppet rig
        if obj and obj.type == 'ARMATURE' and obj.get("is_puppet"):
            gp_name = obj.get("puppet_gp")
            if gp_name and gp_name in bpy.data.objects:
                gp_obj = bpy.data.objects[gp_name]
                bpy.ops.object.select_all(action='DESELECT')
                gp_obj.select_set(True)
                context.view_layer.objects.active = gp_obj
                self.report({'INFO'}, f"Selected {gp_name}")
                return {'FINISHED'}

        self.report({'WARNING'}, "No puppet GP object found")
        return {'CANCELLED'}


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

# Additional classes to register from this module
additional_classes = [
    PUPPET_OT_select_gp,
]


def register():
    bpy.utils.register_class(PUPPET_PT_main_panel)
    for cls in additional_classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(additional_classes):
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(PUPPET_PT_main_panel)
