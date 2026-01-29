# core/rig_builder.py
# ============================================================================
# Functions for creating the puppet armature and Grease Pencil object.
# This is the core of Phase 1b - generating the full puppet structure.
# Optimized for Blender's 2D Animation workflow.
# ============================================================================

import bpy
from mathutils import Vector

from ..constants import (
    BONE_HIERARCHY,
    get_gp_object_name,
    get_y_offset_for_layer,
)


# ----------------------------------------------------------------------------
# 2D ANIMATION MODE SETUP
# ----------------------------------------------------------------------------

def deselect_all_objects():
    """
    Deselect all objects without using operators (context-safe).
    """
    for obj in bpy.data.objects:
        obj.select_set(False)


def setup_2d_view(context):
    """
    Configure the 3D viewport for 2D animation work.
    - Sets view to Front Orthographic
    """
    from mathutils import Quaternion
    import math

    # Get the 3D viewport area and configure it
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Set to Front Orthographic view
                    space.region_3d.view_perspective = 'ORTHO'
                    # Front view quaternion (90 degrees around X axis)
                    space.region_3d.view_rotation = Quaternion(
                        (math.cos(math.pi/4), math.sin(math.pi/4), 0, 0)
                    )
                    break
            break


def frame_puppet_in_view(context, armature_obj):
    """
    Frame the view to show the full puppet.
    Uses direct view manipulation to avoid context issues.
    """
    # Calculate bounding box of armature to frame it
    # Get the armature's bounding box center and size
    bbox_center = armature_obj.location

    # Estimate view distance based on armature size (puppet is ~2 units tall)
    view_distance = 3.0

    # Set view location and distance in all 3D viewports
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Set the view to look at the puppet center
                    space.region_3d.view_location = (
                        bbox_center.x,
                        bbox_center.y,
                        bbox_center.z + 1.0  # Center on middle of puppet (it's ~2 units tall)
                    )
                    space.region_3d.view_distance = view_distance
                    break
            break


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
    Configure the armature to display nicely as a 2D drawing guide.
    - Wire display mode for clear visibility without obscuring drawing
    - In Front enabled so bones show through GP strokes
    - Semi-transparent appearance
    - Custom colors for easy identification
    """
    armature = armature_obj.data

    # Display settings optimized for 2D drawing guide
    armature.display_type = 'WIRE'  # Wire is cleaner for 2D tracing
    armature_obj.show_in_front = True  # Always visible as drawing guide

    # Make armature semi-transparent so it doesn't obscure drawing
    armature_obj.show_wire = True

    # Enable bone colors (available in Blender 4.0+)
    armature.show_bone_colors = True

    # Set a subtle color for the armature (light blue guide color)
    armature_obj.color = (0.2, 0.6, 1.0, 0.5)  # Light blue, 50% alpha


# ----------------------------------------------------------------------------
# COLLECTION MANAGEMENT
# ----------------------------------------------------------------------------

def create_puppet_collection(puppet_name, context):
    """
    Create a Blender collection to organize all GP objects for a puppet.
    Returns the collection.
    """
    col_name = f"{puppet_name}_Parts"
    collection = bpy.data.collections.new(col_name)
    context.scene.collection.children.link(collection)
    return collection


# ----------------------------------------------------------------------------
# PER-OBJECT GREASE PENCIL CREATION
# Each drawable body part gets its own GP object (created on demand).
# This avoids the Blender 5.0 GP v3 layer-switching bug where drawings
# disappear when switching active layers within a single GP object.
# ----------------------------------------------------------------------------

def _get_or_create_shared_material(puppet_name):
    """
    Get or create a shared stroke material for a puppet's GP objects.
    Reuses the same material across all GP objects for consistency.
    """
    stroke_name = f"{puppet_name}_Stroke"

    # Reuse existing material if it exists
    mat = bpy.data.materials.get(stroke_name)
    if mat:
        return mat

    # Create new stroke material
    mat = bpy.data.materials.new(name=stroke_name)

    # Try legacy GP material setup (Blender 4.0-4.2)
    if hasattr(bpy.data.materials, 'create_gpencil_data'):
        try:
            bpy.data.materials.create_gpencil_data(mat)
            mat.grease_pencil.color = (0.0, 0.0, 0.0, 1.0)
            mat.grease_pencil.show_stroke = True
            mat.grease_pencil.show_fill = False
        except Exception:
            pass

    return mat


def create_gp_for_layer(armature_obj, layer_name, context):
    """
    Create a single GP object for one drawable layer.
    Called on-demand when the user first draws a body part.

    The GP object gets:
    - One layer (named after the part)
    - Shared material
    - Parented to the armature
    - Y-offset for z-ordering in front ortho view
    - Added to the puppet's collection
    - Custom properties for identification

    Args:
        armature_obj: The puppet's armature object
        layer_name: The layer identifier (e.g., "Head_Front", "Face_Features")
        context: Blender context

    Returns:
        The created GP object
    """
    puppet_name = armature_obj["puppet_name"]
    gp_name = get_gp_object_name(puppet_name, layer_name)

    # Create GP data block
    if is_gp_v3():
        try:
            if hasattr(bpy.data, 'grease_pencils_v3'):
                gp_data = bpy.data.grease_pencils_v3.new(gp_name)
            else:
                gp_data = bpy.data.grease_pencils.new(gp_name)
        except Exception:
            gp_data = bpy.data.grease_pencils.new(gp_name)
    else:
        gp_data = bpy.data.grease_pencils.new(gp_name)

    gp_obj = bpy.data.objects.new(gp_name, gp_data)

    # Create the single drawing layer
    try:
        if hasattr(gp_data.layers, 'new'):
            try:
                layer = gp_data.layers.new(name=layer_name)
            except TypeError:
                layer = gp_data.layers.new(layer_name)

            if hasattr(layer, 'hide'):
                layer.hide = False
            if hasattr(layer, 'opacity'):
                layer.opacity = 1.0

            # Legacy GP needs an initial frame
            if not is_gp_v3() and hasattr(layer, 'frames'):
                layer.frames.new(1)
    except Exception as e:
        print(f"Puppet Mode: Could not create layer for {layer_name}: {e}")

    # Disable autolock
    if hasattr(gp_data, 'use_autolock_layers'):
        gp_data.use_autolock_layers = False

    # Set active layer
    if gp_data.layers:
        gp_data.layers.active = gp_data.layers[0]

    # Assign shared material
    mat = _get_or_create_shared_material(puppet_name)
    gp_data.materials.append(mat)
    gp_obj.active_material_index = 0

    # Link to puppet's collection (scene collection as fallback)
    col_name = armature_obj.get("puppet_collection", "")
    collection = bpy.data.collections.get(col_name)
    if collection:
        collection.objects.link(gp_obj)
    else:
        context.collection.objects.link(gp_obj)

    # Parent to armature
    gp_obj.parent = armature_obj

    # Y-offset for z-ordering (more negative = rendered in front)
    y_offset = get_y_offset_for_layer(layer_name)
    gp_obj.location = (0, y_offset, 0)

    # Custom properties for identification
    gp_obj["puppet_rig"] = armature_obj.name
    gp_obj["puppet_layer"] = layer_name

    return gp_obj


def find_or_create_gp_for_layer(armature_obj, layer_name, context):
    """
    Find an existing GP object for a layer, or create one on demand.
    This is the main entry point used by the DRAW operator.

    Args:
        armature_obj: The puppet's armature object
        layer_name: The layer identifier (e.g., "Head_Front")
        context: Blender context

    Returns:
        The GP object for this layer
    """
    puppet_name = armature_obj["puppet_name"]
    gp_name = get_gp_object_name(puppet_name, layer_name)

    existing = bpy.data.objects.get(gp_name)
    if existing:
        return existing

    return create_gp_for_layer(armature_obj, layer_name, context)


def get_puppet_gp_objects(armature_obj):
    """
    Get all GP objects belonging to a puppet.
    Returns a list of (gp_obj, layer_name) tuples.
    """
    if not armature_obj:
        return []

    results = []
    for obj in bpy.data.objects:
        if obj.get("puppet_rig") == armature_obj.name and obj.get("puppet_layer"):
            results.append((obj, obj["puppet_layer"]))
    return results


# ----------------------------------------------------------------------------
# PUPPET ASSEMBLY
# ----------------------------------------------------------------------------

def create_puppet(context, base_name="Puppet"):
    """
    Main entry point: Create a puppet with armature and parts collection.
    GP objects are created on-demand when the user clicks DRAW.

    This creates:
    1. An armature with the full bone hierarchy (configured as 2D drawing guide)
    2. A collection to hold GP objects (created later per body part)
    3. Stores custom properties for puppet management
    4. Sets up the view for 2D animation (Front Orthographic)

    Args:
        context: Blender context
        base_name: Base name for the puppet (will be made unique)

    Returns:
        The created armature object
    """
    # Generate unique name
    existing_names = {obj.name for obj in bpy.data.objects}
    puppet_name = get_unique_name(base_name, existing_names)

    # Deselect all objects first (without using operators)
    deselect_all_objects()

    # Create the armature (this will be the "master" object)
    armature_obj = create_armature(puppet_name, context)

    # Create collection for GP objects (populated on-demand)
    collection = create_puppet_collection(puppet_name, context)

    # Store custom properties on armature to identify as puppet
    armature_obj["is_puppet"] = True
    armature_obj["puppet_name"] = puppet_name
    armature_obj["puppet_collection"] = collection.name
    armature_obj["proportions_locked"] = False  # For Phase 1.5

    # Position in 3D view (at world origin, facing -Y)
    armature_obj.location = (0, 0, 0)

    # ----- 2D ANIMATION MODE SETUP -----

    # Set view to Front Orthographic (standard 2D animation view)
    setup_2d_view(context)

    # Frame the puppet in view
    frame_puppet_in_view(context, armature_obj)

    # Select armature and make it active
    deselect_all_objects()
    armature_obj.select_set(True)
    context.view_layer.objects.active = armature_obj

    return armature_obj


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
