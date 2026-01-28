# core/properties.py
# ============================================================================
# Property definitions for Puppet Mode UI state.
# These properties store the user's current selection in the body part selector.
# ============================================================================

import bpy
from bpy.props import (
    EnumProperty,
    StringProperty,
    BoolProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup

from ..constants import (
    UI_BODY_REGIONS,
    GP_LAYER_STRUCTURE,
    HAND_POSES,
    ROTATION_VIEWS_FULL,
    ROTATION_VIEWS_SIMPLE,
    HAND_ROTATION_VIEWS,
)


# ----------------------------------------------------------------------------
# DYNAMIC ENUM CALLBACKS
# These functions generate the dropdown options based on current selection.
# ----------------------------------------------------------------------------

def get_region_items(self, context):
    """Return the body region options (Face, Body, Hands)."""
    return [
        ('FACE', 'Face', 'Head, eyes, eyebrows, mouth'),
        ('BODY', 'Body', 'Torso, arms, legs'),
        ('HANDS', 'Hands', 'Hand poses and views'),
    ]


def get_part_items(self, context):
    """
    Return the body part options based on selected region.
    Dynamically generates items from UI_BODY_REGIONS.
    """
    items = []
    region = self.region

    if region == 'FACE':
        parts = UI_BODY_REGIONS.get('Face', [])
    elif region == 'BODY':
        parts = UI_BODY_REGIONS.get('Body', [])
    elif region == 'HANDS':
        parts = ['Hand_L', 'Hand_R']
    else:
        parts = []

    for part in parts:
        # Create a readable label
        label = part.replace('_', ' ')
        items.append((part, label, f'Select {label}'))

    # Ensure at least one item
    if not items:
        items.append(('NONE', 'None', 'No parts available'))

    return items


def get_rotation_items(self, context):
    """
    Return rotation view options based on selected part.
    Different parts have different rotation options.
    """
    items = []
    part = self.part

    # Determine which rotation views this part supports
    if part in ['Head']:
        rotations = ROTATION_VIEWS_FULL
    elif part in ['Chest', 'Spine', 'Hips']:
        rotations = ROTATION_VIEWS_FULL
    elif part in ['Eyes', 'Eyebrows', 'Mouth']:
        # These use shape keys, not rotation swaps
        rotations = ['Default']
    elif part.startswith('Hand_'):
        rotations = HAND_ROTATION_VIEWS
    elif part.startswith(('Arm_', 'Leg_', 'Foot_')):
        rotations = ROTATION_VIEWS_SIMPLE
    else:
        rotations = ['Front']

    for rot in rotations:
        items.append((rot, rot.replace('_', ' '), f'{rot} view'))

    if not items:
        items.append(('NONE', 'None', 'No rotations available'))

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
    """

    region: EnumProperty(
        name="Body Region",
        description="Select body region to draw",
        items=get_region_items,
        default=0,
    )

    part: EnumProperty(
        name="Body Part",
        description="Select specific body part",
        items=get_part_items,
    )

    rotation: EnumProperty(
        name="Rotation View",
        description="Select rotation angle to draw",
        items=get_rotation_items,
    )

    hand_pose: EnumProperty(
        name="Hand Pose",
        description="Select hand pose (for hands only)",
        items=get_hand_pose_items,
        default=0,
    )


# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

def get_current_layer_name(context):
    """
    Get the GP layer name for the current selection.
    Returns the full layer name like "Head_Front" or "Hand_L_Fist_Back".
    """
    props = context.scene.puppet_selector
    part = props.part
    rotation = props.rotation

    # Special cases
    if part in ['Eyes', 'Eyebrows', 'Mouth']:
        # These parts don't have rotation views
        if part == 'Eyes':
            return 'Eye_L'  # Default to left eye
        elif part == 'Eyebrows':
            return 'Eyebrow_L'
        else:
            return 'Mouth'

    # Hand parts include pose
    if part.startswith('Hand_'):
        pose = props.hand_pose
        return f"{part}_{pose}_{rotation}"

    # Standard parts: Part_Rotation
    return f"{part}_{rotation}"


def is_layer_drawn(gp_obj, layer_name):
    """
    Check if a GP layer has any strokes (has been drawn on).
    Returns True if the layer exists and has content.
    Handles both legacy GP and GP v3 (Blender 5.0+).
    """
    if not gp_obj or not gp_obj.data:
        return False

    # Find the layer
    layers = gp_obj.data.layers
    layer = layers.get(layer_name)

    if not layer:
        return False

    # GP v3 (Blender 5.0+) uses a different structure
    # Try multiple approaches to detect content

    # Method 1: Check frames.strokes (legacy GP)
    if hasattr(layer, 'frames'):
        for frame in layer.frames:
            if hasattr(frame, 'strokes') and len(frame.strokes) > 0:
                return True
            # GP v3 might use 'drawing' instead
            if hasattr(frame, 'drawing'):
                drawing = frame.drawing
                if drawing and hasattr(drawing, 'strokes') and len(drawing.strokes) > 0:
                    return True

    # Method 2: Check if layer has any drawings (GP v3)
    if hasattr(layer, 'current_frame'):
        frame = layer.current_frame
        if frame:
            if hasattr(frame, 'strokes') and len(frame.strokes) > 0:
                return True
            if hasattr(frame, 'drawing'):
                drawing = frame.drawing
                if drawing and hasattr(drawing, 'strokes') and len(drawing.strokes) > 0:
                    return True

    # Method 3: Direct drawing access (some GP v3 versions)
    if hasattr(gp_obj.data, 'drawings'):
        # GP v3 stores drawings separately
        for drawing in gp_obj.data.drawings:
            if hasattr(drawing, 'strokes') and len(drawing.strokes) > 0:
                # This drawing has content, but we'd need to check if it's linked to our layer
                # For simplicity, we'll use frame-based checking above
                pass

    return False


def count_drawn_layers(gp_obj):
    """
    Count how many layers have been drawn on.
    Returns (drawn_count, total_count).
    """
    if not gp_obj or not gp_obj.data:
        return 0, 0

    drawn = 0
    total = len(gp_obj.data.layers)

    # Use is_layer_drawn for consistent checking
    for layer in gp_obj.data.layers:
        if is_layer_drawn(gp_obj, layer.name):
            drawn += 1

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
