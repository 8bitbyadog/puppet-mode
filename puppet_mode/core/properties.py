# core/properties.py
# ============================================================================
# Property definitions for Puppet Mode UI state.
# These properties store the user's current selection in the body part selector.
#
# REDESIGNED: Simplified to work with new layer structure.
# - character_view: Which angle we're working in (Front, Quarter, Profile)
# - part: Which body part to draw
# - reference_opacity: How visible other parts are while drawing
# ============================================================================

import bpy
from bpy.props import (
    EnumProperty,
    StringProperty,
    BoolProperty,
    FloatProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup

from ..constants import (
    UI_BODY_REGIONS,
    GP_LAYER_STRUCTURE,
    HAND_POSES,
    CHARACTER_VIEWS,
    DRAWABLE_PARTS,
    VIEW_DEPENDENT_PARTS,
    VIEW_INDEPENDENT_PARTS,
    get_gp_object_name,
    get_all_layer_names,
    # Legacy compatibility
    ROTATION_VIEWS_FULL,
    ROTATION_VIEWS_SIMPLE,
    HAND_ROTATION_VIEWS,
)


# ----------------------------------------------------------------------------
# DYNAMIC ENUM CALLBACKS
# These functions generate the dropdown options based on current selection.
# ----------------------------------------------------------------------------

def get_character_view_items(self, context):
    """Return character view options (Front, Quarter, Profile)."""
    return [
        ('Front', 'Front', 'Front view of character'),
        ('Quarter_L', 'Quarter L', 'Left quarter view (3/4 angle)'),
        ('Quarter_R', 'Quarter R', 'Right quarter view (3/4 angle)'),
        ('Profile_L', 'Profile L', 'Left side profile'),
        ('Profile_R', 'Profile R', 'Right side profile'),
    ]


def get_region_items(self, context):
    """Return the body region options (Face, Body, Hands)."""
    return [
        ('FACE', 'Face', 'Head and facial features'),
        ('BODY', 'Body', 'Torso, arms, legs'),
        ('HANDS', 'Hands', 'Hand poses'),
    ]


def get_part_items(self, context):
    """
    Return the body part options based on selected region.
    SIMPLIFIED: Uses new DRAWABLE_PARTS structure.
    """
    items = []
    region = self.region

    if region == 'FACE':
        parts = UI_BODY_REGIONS.get('Face', [])
    elif region == 'BODY':
        parts = UI_BODY_REGIONS.get('Body', [])
    elif region == 'HANDS':
        parts = UI_BODY_REGIONS.get('Hands', [])
    else:
        parts = []

    for part in parts:
        # Create a readable label
        label = part.replace('_', ' ').replace('L', 'Left').replace('R', 'Right')
        # Better labels
        if part == "Face_Features":
            label = "Face (Eyes, Brows)"
        elif part == "Arm_L":
            label = "Left Arm"
        elif part == "Arm_R":
            label = "Right Arm"
        elif part == "Leg_L":
            label = "Left Leg"
        elif part == "Leg_R":
            label = "Right Leg"
        elif part == "Hand_L":
            label = "Left Hand"
        elif part == "Hand_R":
            label = "Right Hand"
        elif part == "Foot_L":
            label = "Left Foot"
        elif part == "Foot_R":
            label = "Right Foot"

        items.append((part, label, f'Draw {label}'))

    if not items:
        items.append(('NONE', 'None', 'No parts available'))

    return items


def get_rotation_items(self, context):
    """
    Return rotation view options based on selected part.
    SIMPLIFIED: Most parts now use character_view instead.
    """
    items = []
    part = self.part

    # View-dependent parts don't need rotation selector
    # (they use character_view instead)
    if part in VIEW_DEPENDENT_PARTS:
        items.append(('USE_VIEW', '(Uses Character View)', 'This part uses the character view setting'))
    elif part in VIEW_INDEPENDENT_PARTS:
        if part.startswith('Hand_'):
            # Hands have pose variants
            for pose in HAND_POSES:
                items.append((pose, pose, f'{pose} hand pose'))
        else:
            items.append(('Default', 'Default', 'Single view'))
    else:
        items.append(('Default', 'Default', 'Default view'))

    if not items:
        items.append(('NONE', 'None', 'No options'))

    return items


def get_hand_pose_items(self, context):
    """Return hand pose options."""
    items = []
    for pose in HAND_POSES:
        items.append((pose, pose, f'{pose} hand pose'))
    return items


# ----------------------------------------------------------------------------
# PROPERTY GROUP
# ----------------------------------------------------------------------------

class PUPPET_PG_selector(PropertyGroup):
    """
    Property group storing the current body part selection state.
    Registered on Scene so it persists across the session.

    REDESIGNED: Simplified workflow with character_view as primary selector.
    """

    # PRIMARY: Which angle of the character are we working on?
    character_view: EnumProperty(
        name="Character View",
        description="Which angle of the character to draw",
        items=get_character_view_items,
        default=0,
    )

    # Body region filter (Face/Body/Hands)
    region: EnumProperty(
        name="Body Region",
        description="Filter parts by body region",
        items=get_region_items,
        default=0,
    )

    # Which part to draw
    part: EnumProperty(
        name="Body Part",
        description="Select specific body part to draw",
        items=get_part_items,
    )

    # For parts that have variants (like hand poses)
    rotation: EnumProperty(
        name="Variant",
        description="Select variant (for hands: pose)",
        items=get_rotation_items,
    )

    hand_pose: EnumProperty(
        name="Hand Pose",
        description="Select hand pose",
        items=get_hand_pose_items,
        default=0,
    )

    # Reference opacity while drawing
    reference_opacity: FloatProperty(
        name="Reference Opacity",
        description="How visible other parts are while drawing",
        default=0.3,
        min=0.1,
        max=0.8,
        step=5,
    )

    # Legacy: Onion skin settings (now "reference" mode)
    onion_skin_enabled: BoolProperty(
        name="Show References",
        description="Show other drawn parts while drawing",
        default=True,  # ON by default now
    )

    onion_skin_opacity: FloatProperty(
        name="Reference Opacity",
        description="Opacity of reference layers",
        default=0.3,
        min=0.1,
        max=0.5,
        step=5,
    )


# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

def get_current_layer_name(context):
    """
    Get the layer name for the current selection.
    This also serves as the GP object name suffix in the per-object architecture.

    Examples:
    - Head + Front view -> "Head_Front"
    - Body + Quarter_L view -> "Body_Quarter_L"
    - Face_Features (view-independent) -> "Face_Features"
    - Hand_L + Open pose -> "Hand_L_Open"
    """
    props = context.scene.puppet_selector
    part = props.part
    view = props.character_view

    # View-independent parts
    if part in ['Face_Features', 'Mouth']:
        return part

    if part in ['Foot_L', 'Foot_R']:
        return part

    # Hand parts use pose instead of view
    if part.startswith('Hand_'):
        pose = props.hand_pose
        return f"{part}_{pose}"

    # View-dependent parts: combine part + view
    if part in VIEW_DEPENDENT_PARTS:
        return f"{part}_{view}"

    # Fallback
    return part


def get_view_layer_names(context):
    """
    Get layer names relevant to the current view + hand pose.
    Returns a set of layer names that should be visible for the current view.
    """
    from ..constants import get_active_layers_for_view
    props = context.scene.puppet_selector
    return set(get_active_layers_for_view(props.character_view, props.hand_pose))


def is_layer_drawn(armature_obj, layer_name):
    """
    Check if a body part has been drawn.
    In the per-object architecture, a part is drawn if its GP object exists.
    """
    if not armature_obj:
        return False
    puppet_name = armature_obj.get("puppet_name", "")
    if not puppet_name:
        return False
    gp_name = get_gp_object_name(puppet_name, layer_name)
    return gp_name in bpy.data.objects


def count_drawn_parts(armature_obj):
    """
    Count how many parts have been drawn (have GP objects).
    Returns (drawn_count, total_count).
    """
    if not armature_obj:
        return 0, 0

    all_layers = get_all_layer_names()
    total = len(all_layers)
    drawn = sum(1 for ln in all_layers if is_layer_drawn(armature_obj, ln))
    return drawn, total


# ----------------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------------

def register():
    bpy.utils.register_class(PUPPET_PG_selector)
    bpy.types.Scene.puppet_selector = PointerProperty(type=PUPPET_PG_selector)


def unregister():
    del bpy.types.Scene.puppet_selector
    bpy.utils.unregister_class(PUPPET_PG_selector)
