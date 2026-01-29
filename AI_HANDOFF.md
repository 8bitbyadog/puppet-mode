# AI Handoff: Persistent Drawings Bug in Puppet Mode

## Project Overview

**Puppet Mode** is a Blender add-on (Python) for real-time 2D character puppeteering using Grease Pencil. It's inspired by Adobe Character Animator. The add-on creates an armature skeleton as a drawing guide, and the user draws body parts (Head, Body, Arms, etc.) on separate layers/objects for different character views (Front, Quarter, Profile).

- **Repo**: https://github.com/8bitbyadog/puppet-mode
- **Target**: Blender 5.0 (GP v3 / Grease Pencil v3)
- **Also supports**: Blender 4.0-4.2 (legacy GP)
- **Language**: Python (Blender add-on using `bpy` API)
- **Current version**: 0.2.0 (Phase 1c)

## The Bug

**When the user draws on one body part (e.g., Head) and then clicks DRAW on a different body part (e.g., Eyes/Face_Features), the previous drawing disappears.**

The user's workflow:
1. Select "Head" in the UI, click DRAW -> draws the head -> drawing appears fine
2. Select "Face Features" (eyes), click DRAW -> the head drawing vanishes
3. Switch back to Head -> the head drawing is still gone

**The user wants**: All drawings to persist. Drawing on Eyes should NOT affect the Head drawing. Each part's art should stay visible (at reduced opacity as reference) when drawing other parts.

## What We Know

### The Root Cause

The user discovered that **drawings persist when using separate Grease Pencil objects** (e.g., two completely different puppet rigs) but **disappear when switching layers within a single GP object**. This points to a Blender 5.0 Grease Pencil v3 issue with layer switching.

### Blender 5.0 GP v3 API Details

- Object type: `'GREASEPENCIL'` (not `'GPENCIL'`)
- Paint mode: `'PAINT_GREASE_PENCIL'` (not `'PAINT_GPENCIL'`)
- GP data: `bpy.data.grease_pencils_v3` (not `bpy.data.grease_pencils`)
- `GreasePencilLayer.opacity` **defaults to 0.0** in the API (must explicitly set to 1.0)
- `GreasePencilLayer.current_frame()` is a **method** (not a property like legacy GP)
- `GreasePencil.use_autolock_layers` exists and can interfere
- Viewport overlay `use_grease_pencil_fade_layers` can hide non-active layers

## Approaches Tried (All Failed)

### Attempt 1: View-Aware Layer Management
- Added view filtering so only layers relevant to the current character view are shown
- Added reliable drawn-layer tracking using custom properties on the GP object
- Added `get_active_layers_for_view()` to `constants.py`
- Added `get_drawn_layers_set()`, `add_to_drawn_layers()` tracking to `properties.py`
- **Result**: Still disappeared. The tracking was correct but the visual bug persisted.

### Attempt 2: GP v3 API Workarounds
- Researched Blender 5.0 GP v3 API specifics
- Added `already_painting` check to avoid unnecessary mode transitions
- Applied layer visibility TWICE (before AND after entering paint mode) because GP v3 resets layer state on mode transition
- Disabled `use_autolock_layers` on GP data
- Disabled `use_gpencil_fade_layers` / `use_grease_pencil_fade_layers` viewport overlay
- Set `layer.opacity = 1.0` explicitly on all layers during creation
- Fixed `current_frame()` method vs property handling
- **Result**: Still disappeared. The mode transition workarounds didn't help.

### Attempt 3: Per-Object GP Architecture (Current State)
- Completely rewrote the architecture so each body part gets its own GP object
- GP objects created on-demand when user clicks DRAW
- Each GP object has exactly one layer (no layer switching needed)
- GP objects parented to the armature, organized in a Blender collection
- Y-offset on each GP object controls z-ordering in front orthographic view
- "Drawn" detection is simply checking if the GP object exists (no stroke scanning)
- Other parts shown at reduced opacity by setting `gp_obj.data.layers[0].opacity`
- Non-relevant parts hidden via `gp_obj.hide_viewport = True`
- **Result**: User reports the same bug still occurs (9th attempt).

## Current Architecture (After Attempt 3)

### File Structure
```
puppet_mode/
  __init__.py           - Add-on registration
  constants.py          - All constants, bone hierarchy, layer structure, helpers
  core/
    properties.py       - UI property group, layer name resolution, drawn detection
    rig_builder.py      - Armature creation, GP object creation (per-object)
  operators/
    create_puppet.py    - "Create New Puppet" operator
    draw_part.py        - DRAW and VIEW operators (core interaction)
  panels/
    main_panel.py       - N-panel UI with view selector, part selector, outliner
```

### Key Functions

- `create_puppet()` in `rig_builder.py` - Creates armature + empty collection. Returns armature only.
- `find_or_create_gp_for_layer()` in `rig_builder.py` - On-demand GP object creation
- `get_puppet_gp_objects()` in `rig_builder.py` - Finds all GP objects for a puppet
- `PUPPET_OT_draw_part.execute()` in `draw_part.py` - The core DRAW operator
- `PUPPET_OT_view_part.execute()` in `draw_part.py` - Shows assembled character
- `get_current_layer_name()` in `properties.py` - Resolves part + view to layer name
- `get_view_layer_names()` in `properties.py` - Gets all layers for current view
- `is_layer_drawn()` in `properties.py` - Checks if GP object exists

### How DRAW Works Now
1. User selects a body part + view in the UI
2. Clicks DRAW
3. `find_or_create_gp_for_layer()` gets/creates a GP object for that part
4. All other puppet GP objects: set to reference opacity or hidden
5. Target GP object: selected, made active, enters `PAINT_GREASE_PENCIL` mode

### Custom Properties
- Armature: `is_puppet`, `puppet_name`, `puppet_collection`
- Each GP object: `puppet_rig` (armature name), `puppet_layer` (layer identifier)

## What to Investigate Next

1. **Is the drawing actually being lost, or just hidden?** Check in Blender's Outliner after the bug triggers - does the GP object still have strokes? This would tell us if it's a rendering/visibility issue vs. actual data loss.

2. **Is `bpy.ops.object.mode_set()` the culprit?** The mode transition from OBJECT to PAINT_GREASE_PENCIL might be destroying/invalidating data on other GP objects. Try staying in OBJECT mode and not entering paint mode to see if drawings persist.

3. **Is `hide_viewport` or opacity changes on other GP objects causing issues?** Maybe modifying any property on a GP object while another is in paint mode triggers the bug. Try the DRAW operator WITHOUT setting visibility/opacity on other objects.

4. **Test with pure Blender UI (no add-on)**: Create two separate GP objects manually in Blender 5.0. Draw on one, switch to the other, draw on it. Does the first drawing persist? If not, this is a Blender bug, not an add-on bug.

5. **Frame/keyframe issues**: GP v3 stores drawings in frames. Make sure frame 1 exists and is correct. The drawing might be on a different frame than expected.

6. **Check if `context.view_layer.objects.active = target_gp` triggers data invalidation** on the previously active GP object.

7. **Consider using `bpy.ops.gpencil.draw()` or `bpy.ops.grease_pencil.draw()`** instead of mode switching, if such operators exist in Blender 5.0.

## Key Constants

```python
DRAWABLE_PARTS = [
    "Face_Features", "Mouth", "Head", "Body",
    "Arm_L", "Arm_R", "Hand_L", "Hand_R",
    "Leg_L", "Leg_R", "Foot_L", "Foot_R",
]
VIEW_DEPENDENT_PARTS = ["Head", "Body", "Arm_L", "Arm_R", "Leg_L", "Leg_R"]
VIEW_INDEPENDENT_PARTS = ["Face_Features", "Mouth", "Hand_L", "Hand_R", "Foot_L", "Foot_R"]
CHARACTER_VIEWS = ["Front", "Quarter_L", "Quarter_R", "Profile_L", "Profile_R"]
```

Layer names are formed by combining part + view: `Head_Front`, `Body_Quarter_L`, etc.
GP object names: `{PuppetName}_{LayerName}` e.g., `Puppet_Head_Front`.

## User Notes

- The user is testing on Blender 5.0
- The user confirmed drawings persist between completely separate puppet rigs (separate armature+GP pairs), but not within the same puppet
- The user is patient and appreciative but has been through 9 failed attempts
- Priority: Get drawings to persist when switching between body parts within the same puppet
