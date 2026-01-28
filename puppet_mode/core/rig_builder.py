# core/rig_builder.py
# ============================================================================
# Functions for creating the puppet armature and Grease Pencil object.
# This is the core of Phase 1b - generating the full puppet structure.
# ============================================================================

import bpy
from mathutils import Vector

# Import our constants
import sys
import os

# Get the parent directory to import constants
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ..constants import (
    BONE_HIERARCHY,
    GP_LAYER_STRUCTURE,
    LAYER_TO_BONE,
    get_all_layer_names,
)


# ----------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ----------------------------------------------------------------------------

def get_unique_name(base_name, existing_names):
    """
    Generate a unique name by appending a number suffix.
    E.g., "Puppet" -> "Puppet_001", "Puppet_002", etc.
    """
    # Check if base name already has a numeric suffix
    if base_name in existing_names:
        counter = 1
        while f"{base_name}_{counter:03d}" in existing_names:
            counter += 1
        return f"{base_name}_{counter:03d}"
    return base_name


def get_blender_version():
    """Return Blender version as a tuple (major, minor, patch)."""
    return bpy.app.version


def is_gp_v3():
    """
    Check if we're using Grease Pencil v3 (Blender 4.3+).
    GP v3 has a different API structure.
    """
    version = get_blender_version()
    return version >= (4, 3, 0)


# ----------------------------------------------------------------------------
# ARMATURE CREATION
# ----------------------------------------------------------------------------

def create_armature(name, context):
    """
    Create the puppet armature with all bones defined in BONE_HIERARCHY.

    Args:
        name: Base name for the armature (e.g., "Puppet_001")
        context: Blender context

    Returns:
        The created armature object
    """
    # Create armature data and object
    armature_data = bpy.data.armatures.new(f"{name}_Rig")
    armature_obj = bpy.data.objects.new(f"{name}_Rig", armature_data)

    # Link to scene
    context.collection.objects.link(armature_obj)

    # Make active and enter edit mode to add bones
    context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    # Build bones recursively from hierarchy
    _build_bones_recursive(armature_data, BONE_HIERARCHY, parent_bone=None)

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Configure armature display for use as drawing guide
    _configure_armature_display(armature_obj)

    return armature_obj


def _build_bones_recursive(armature_data, hierarchy, parent_bone):
    """
    Recursively create bones from the hierarchy dictionary.

    Args:
        armature_data: The armature data block
        hierarchy: Dictionary of bone definitions
        parent_bone: Parent edit bone (or None for root)
    """
    for bone_name, bone_data in hierarchy.items():
        # Create the bone
        bone = armature_data.edit_bones.new(bone_name)

        # Set head and tail positions
        bone.head = Vector(bone_data["head"])
        bone.tail = Vector(bone_data["tail"])

        # Set parent if provided
        if parent_bone is not None:
            bone.parent = parent_bone
            # Use connected for chain bones (tail of parent = head of child)
            if parent_bone.tail == bone.head:
                bone.use_connect = True

        # Recursively create children
        if bone_data.get("children"):
            _build_bones_recursive(armature_data, bone_data["children"], bone)


def _configure_armature_display(armature_obj):
    """
    Configure the armature to display nicely as a drawing guide.
    - Stick display mode for clean visibility
    - In Front enabled so bones show through GP strokes
    - Custom colors for easy identification
    """
    armature = armature_obj.data

    # Display settings
    armature.display_type = 'STICK'  # Clean, minimal bone display
    armature_obj.show_in_front = True  # Always visible as drawing guide

    # Enable bone colors (available in Blender 4.0+)
    armature.show_bone_colors = True


# ----------------------------------------------------------------------------
# GREASE PENCIL CREATION
# ----------------------------------------------------------------------------

def create_grease_pencil(name, context):
    """
    Create the Grease Pencil object with all layers defined in GP_LAYER_STRUCTURE.

    Args:
        name: Base name for the GP object (e.g., "Puppet_001")
        context: Blender context

    Returns:
        The created GP object
    """
    if is_gp_v3():
        return _create_gp_v3(name, context)
    else:
        return _create_gp_legacy(name, context)


def _create_gp_legacy(name, context):
    """
    Create GP object using legacy API (Blender 4.0 - 4.2).
    """
    # Create GP data and object
    gp_data = bpy.data.grease_pencils.new(name)
    gp_obj = bpy.data.objects.new(name, gp_data)

    # Link to scene
    context.collection.objects.link(gp_obj)

    # Create all layers from our structure
    # Layers are created in reverse order because GP layers stack bottom-to-top
    all_layers = get_all_layer_names()
    for layer_name in reversed(all_layers):
        layer = gp_data.layers.new(name=layer_name, set_active=False)
        # Initialize with one empty frame at frame 1
        layer.frames.new(1)
        # Default to hidden except front views
        layer.hide = not layer_name.endswith("_Front")

    # Set the first layer as active
    if gp_data.layers:
        gp_data.layers.active = gp_data.layers[0]

    return gp_obj


def _create_gp_v3(name, context):
    """
    Create GP object using Grease Pencil v3 API (Blender 4.3+).
    GP v3 uses a different data structure with layer groups.
    """
    # In Blender 4.3+, GP uses the new grease_pencil type
    # The API is: bpy.data.grease_pencils_v3.new() or similar
    # For now, we attempt the new API with fallback

    try:
        # Try the v3 API first
        gp_data = bpy.data.grease_pencils_v3.new(name)
    except AttributeError:
        # Fallback: In some 4.3 builds, it might still be grease_pencils
        # but with the new layer structure
        gp_data = bpy.data.grease_pencils.new(name)

    gp_obj = bpy.data.objects.new(name, gp_data)
    context.collection.objects.link(gp_obj)

    # Create layers - GP v3 layer creation
    # In v3, layers are accessed differently
    all_layers = get_all_layer_names()

    for layer_name in reversed(all_layers):
        # v3 API: gp_data.layers.new(name)
        try:
            layer = gp_data.layers.new(name=layer_name)
        except TypeError:
            # Some versions need different arguments
            layer = gp_data.layers.new(layer_name)

        # Default visibility: only _Front views visible
        layer.hide = not layer_name.endswith("_Front")

    return gp_obj


# ----------------------------------------------------------------------------
# PUPPET ASSEMBLY
# ----------------------------------------------------------------------------

def create_puppet(context, base_name="Puppet"):
    """
    Main entry point: Create a complete puppet with armature and GP object.

    This creates:
    1. A Grease Pencil object with all drawable layers
    2. An armature with the full bone hierarchy
    3. Parents the GP object to the armature
    4. Stores custom properties for puppet management

    Args:
        context: Blender context
        base_name: Base name for the puppet (will be made unique)

    Returns:
        tuple: (gp_object, armature_object)
    """
    # Generate unique name
    existing_names = {obj.name for obj in bpy.data.objects}
    puppet_name = get_unique_name(base_name, existing_names)

    # Deselect all objects first
    bpy.ops.object.select_all(action='DESELECT')

    # Create the armature (this will be the "master" object)
    armature_obj = create_armature(puppet_name, context)

    # Create the Grease Pencil object
    gp_obj = create_grease_pencil(puppet_name, context)

    # Parent GP to armature
    gp_obj.parent = armature_obj

    # Store custom properties on armature to identify as puppet
    armature_obj["is_puppet"] = True
    armature_obj["puppet_name"] = puppet_name
    armature_obj["puppet_gp"] = gp_obj.name
    armature_obj["proportions_locked"] = False  # For Phase 1.5

    # Store reference on GP object back to armature
    gp_obj["puppet_rig"] = armature_obj.name

    # Select both objects, make armature active
    gp_obj.select_set(True)
    armature_obj.select_set(True)
    context.view_layer.objects.active = armature_obj

    # Position in 3D view (at world origin, facing -Y)
    armature_obj.location = (0, 0, 0)

    return gp_obj, armature_obj


def get_puppets_in_scene():
    """
    Find all puppet rigs in the current scene.

    Returns:
        List of armature objects that are puppets
    """
    puppets = []
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and obj.get("is_puppet"):
            puppets.append(obj)
    return puppets
