# core/rig_builder.py
# ============================================================================
# Functions for creating the puppet armature and Grease Pencil object.
# This is the core of Phase 1b - generating the full puppet structure.
# Optimized for Blender's 2D Animation workflow.
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
# GREASE PENCIL CREATION
# ----------------------------------------------------------------------------

def create_grease_pencil(name, context):
    """
    Create the Grease Pencil object with all layers defined in GP_LAYER_STRUCTURE.
    Includes default materials ready for 2D drawing.

    Args:
        name: Base name for the GP object (e.g., "Puppet_001")
        context: Blender context

    Returns:
        The created GP object
    """
    if is_gp_v3():
        gp_obj = _create_gp_v3(name, context)
    else:
        gp_obj = _create_gp_legacy(name, context)

    # Add default drawing materials
    _setup_gp_materials(gp_obj)

    return gp_obj


def _setup_gp_materials(gp_obj):
    """
    Set up default materials for the Grease Pencil object.
    Creates a basic stroke material ready for drawing.
    Handles both legacy GP and GP v3 (Blender 4.3+/5.0+).
    """
    try:
        # Try legacy GP material setup (Blender 4.0-4.2)
        if hasattr(bpy.data.materials, 'create_gpencil_data'):
            _setup_gp_materials_legacy(gp_obj)
        else:
            # GP v3 in Blender 5.0+ may not need separate material setup
            # The GP object should work with standard materials
            _setup_gp_materials_v3(gp_obj)
    except Exception as e:
        # If material setup fails, just skip it - user can add materials manually
        print(f"Puppet Mode: Could not set up GP materials: {e}")


def _setup_gp_materials_legacy(gp_obj):
    """
    Set up GP materials using legacy API (Blender 4.0-4.2).
    """
    # Create a default black stroke material
    mat_stroke = bpy.data.materials.new(name=f"{gp_obj.name}_Stroke")
    bpy.data.materials.create_gpencil_data(mat_stroke)

    # Configure stroke material
    mat_stroke.grease_pencil.color = (0.0, 0.0, 0.0, 1.0)  # Black
    mat_stroke.grease_pencil.show_stroke = True
    mat_stroke.grease_pencil.show_fill = False

    # Create a fill material
    mat_fill = bpy.data.materials.new(name=f"{gp_obj.name}_Fill")
    bpy.data.materials.create_gpencil_data(mat_fill)

    # Configure fill material
    mat_fill.grease_pencil.show_stroke = True
    mat_fill.grease_pencil.show_fill = True
    mat_fill.grease_pencil.fill_color = (0.8, 0.8, 0.8, 1.0)  # Light gray fill
    mat_fill.grease_pencil.color = (0.0, 0.0, 0.0, 1.0)  # Black stroke

    # Assign materials to GP object
    gp_obj.data.materials.append(mat_stroke)
    gp_obj.data.materials.append(mat_fill)

    # Set stroke as active material (index 0)
    gp_obj.active_material_index = 0


def _setup_gp_materials_v3(gp_obj):
    """
    Set up GP materials for Grease Pencil v3 (Blender 4.3+/5.0+).
    GP v3 uses a different material system.
    """
    # In GP v3, materials work differently
    # Try to create materials that are compatible with the new system
    try:
        # Create stroke material
        mat_stroke = bpy.data.materials.new(name=f"{gp_obj.name}_Stroke")

        # GP v3 may use grease_pencil_v3 or a different attribute
        if hasattr(mat_stroke, 'grease_pencil'):
            bpy.data.materials.create_gpencil_data(mat_stroke)
            mat_stroke.grease_pencil.color = (0.0, 0.0, 0.0, 1.0)
            mat_stroke.grease_pencil.show_stroke = True
            mat_stroke.grease_pencil.show_fill = False

        gp_obj.data.materials.append(mat_stroke)
        gp_obj.active_material_index = 0

    except Exception as e:
        print(f"Puppet Mode: GP v3 material setup skipped: {e}")


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
    Create GP object using Grease Pencil v3 API (Blender 4.3+/5.0+).
    GP v3 uses a different data structure.
    """
    gp_data = None
    gp_obj = None

    # Try different API approaches for GP v3
    # Blender 5.0 uses bpy.data.grease_pencils_v3
    try:
        if hasattr(bpy.data, 'grease_pencils_v3'):
            gp_data = bpy.data.grease_pencils_v3.new(name)
        else:
            gp_data = bpy.data.grease_pencils.new(name)
    except Exception as e:
        print(f"Puppet Mode: GP data creation error: {e}")
        # Last resort fallback
        gp_data = bpy.data.grease_pencils.new(name)

    gp_obj = bpy.data.objects.new(name, gp_data)
    context.collection.objects.link(gp_obj)

    # Create layers - GP v3 layer creation
    all_layers = get_all_layer_names()

    for layer_name in reversed(all_layers):
        try:
            # Try different layer creation signatures
            if hasattr(gp_data.layers, 'new'):
                try:
                    layer = gp_data.layers.new(name=layer_name)
                except TypeError:
                    layer = gp_data.layers.new(layer_name)

                # Default visibility: only _Front views visible
                if hasattr(layer, 'hide'):
                    layer.hide = not layer_name.endswith("_Front")
        except Exception as e:
            print(f"Puppet Mode: Could not create layer {layer_name}: {e}")

    return gp_obj


# ----------------------------------------------------------------------------
# PUPPET ASSEMBLY
# ----------------------------------------------------------------------------

def create_puppet(context, base_name="Puppet"):
    """
    Main entry point: Create a complete puppet with armature and GP object.
    Optimized for Blender's 2D Animation workflow.

    This creates:
    1. A Grease Pencil object with all drawable layers and default materials
    2. An armature with the full bone hierarchy (configured as 2D drawing guide)
    3. Parents the GP object to the armature
    4. Stores custom properties for puppet management
    5. Sets up the view for 2D animation (Front Orthographic)

    Args:
        context: Blender context
        base_name: Base name for the puppet (will be made unique)

    Returns:
        tuple: (gp_object, armature_object)
    """
    # Generate unique name
    existing_names = {obj.name for obj in bpy.data.objects}
    puppet_name = get_unique_name(base_name, existing_names)

    # Deselect all objects first (without using operators)
    deselect_all_objects()

    # Create the armature (this will be the "master" object)
    armature_obj = create_armature(puppet_name, context)

    # Create the Grease Pencil object (includes default materials)
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

    # Position in 3D view (at world origin, facing -Y)
    armature_obj.location = (0, 0, 0)

    # ----- 2D ANIMATION MODE SETUP -----

    # Set view to Front Orthographic (standard 2D animation view)
    setup_2d_view(context)

    # Frame the puppet in view
    frame_puppet_in_view(context, armature_obj)

    # Select GP object and make it active (ready to draw)
    deselect_all_objects()
    gp_obj.select_set(True)
    context.view_layer.objects.active = gp_obj

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
