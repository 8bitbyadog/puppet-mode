# Puppet Mode

A Blender 4.x add-on for real-time 2D character puppeteering using Grease Pencil.

**Goal:** Recreate Adobe Character Animator's workflow in Blender — rig-first drawing, rotation view swapping, and real-time performance via tracking input.

## Current Status: Phase 1 (Foundation)

- [x] Add-on registration and UI panel
- [x] "Create New Puppet" operator
- [x] Full armature skeleton (63 bones)
- [x] Grease Pencil object with 87 drawable layers
- [ ] Body part selector UI (Phase 1c)
- [ ] Body type proportion sliders (Phase 1.5)
- [ ] Rotation swap drivers (Phase 2)
- [ ] OSC input (Phase 3)
- [ ] Recording/playback (Phase 4)

---

## Installation

### Step 1: Find Your Blender Addons Folder

**macOS:**
```
~/Library/Application Support/Blender/4.x/scripts/addons/
```

**Windows:**
```
%APPDATA%\Blender Foundation\Blender\4.x\scripts\addons\
```

**Linux:**
```
~/.config/blender/4.x/scripts/addons/
```

> Replace `4.x` with your Blender version (e.g., `4.0`, `4.1`, `4.2`, `4.3`).

If the `addons` folder doesn't exist, create it.

### Step 2: Copy the Add-on

Copy the entire `puppet_mode` folder into the addons directory:

```
addons/
└── puppet_mode/
    ├── __init__.py
    ├── constants.py
    ├── core/
    ├── operators/
    ├── panels/
    └── presets/
```

### Step 3: Enable in Blender

1. Open Blender
2. Go to **Edit > Preferences > Add-ons**
3. Search for "Puppet Mode"
4. Check the checkbox to enable it
5. Close Preferences

---

## Quick Start: Testing the Add-on

### 1. Open the Puppet Mode Panel

1. In the 3D Viewport, press `N` to open the sidebar
2. Click the **"Puppet Mode"** tab

You should see the panel with a "Create New Puppet" button.

### 2. Create Your First Puppet

1. Click **"Create New Puppet"**
2. Two objects will be created:
   - `Puppet_Rig` — The armature (bone skeleton)
   - `Puppet` — The Grease Pencil object (for drawing)

### 3. Explore the Structure

**View the Armature:**
1. Select `Puppet_Rig` in the Outliner
2. Press `Tab` to enter Edit Mode
3. You'll see the full skeleton: spine, head, arms, hands (with fingers), legs

**View the GP Layers:**
1. Select `Puppet` in the Outliner
2. Open the **Grease Pencil Layers** panel (in Properties > Object Data)
3. You'll see 87 layers organized by body part and rotation view

### 4. Test Drawing (Manual Method)

Until Phase 1c is complete, you can manually test drawing:

1. Select the `Puppet` GP object
2. In the GP Layers panel, find a layer like `Head_Front`
3. Click the eye icon to make it visible
4. Enter **Draw Mode** (dropdown in top-left, or press `D` then `D`)
5. Draw on the layer

---

## Understanding the Structure

### Armature Bones (63 total)

```
Root
└── Spine
    ├── Chest
    │   ├── Neck → Head → Eye_L, Eye_R, Eyebrow_L, Eyebrow_R, Jaw
    │   ├── Shoulder_L → Arm_Upper_L → Arm_Lower_L → Hand_L → (5 fingers × 3 bones each)
    │   └── Shoulder_R → Arm_Upper_R → Arm_Lower_R → Hand_R → (5 fingers × 3 bones each)
    └── Hips
        ├── Leg_Upper_L → Leg_Lower_L → Foot_L
        └── Leg_Upper_R → Leg_Lower_R → Foot_R
```

### Grease Pencil Layers (87 total)

Layers are named by: `{BodyPart}_{RotationView}` or `{BodyPart}_{Pose}_{RotationView}`

**Rotation Views:**
- `Front`, `3Q_L`, `3Q_R`, `Side_L`, `Side_R`, `Back` (for head, torso)
- `Front`, `Side` (for arms, legs)
- `Front`, `Back` (for hands)

**Hand Poses:**
- `Open`, `Fist`, `Point`, `Relaxed`, `Spread`

**Examples:**
- `Head_Front` — Head from the front
- `Head_3Q_L` — Head at 3/4 angle, turned left
- `Hand_L_Fist_Front` — Left hand, fist pose, front view
- `Arm_Upper_R_Side` — Right upper arm, side view

---

## Troubleshooting

### Add-on doesn't appear in preferences
- Make sure you copied the entire `puppet_mode` folder, not just individual files
- Check that `__init__.py` is directly inside `puppet_mode/`

### Error when enabling add-on
- Check Blender's console for error messages:
  - **macOS:** Window > Toggle System Console (or run Blender from Terminal)
  - **Windows:** Window > Toggle System Console
- Common issue: Blender version mismatch (requires 4.0+)

### "Create New Puppet" does nothing
- Check the console for errors
- Make sure you're in Object Mode before clicking

### Can't see the armature
- The armature might be at the world origin (0, 0, 0)
- Press `Numpad .` to focus on selected object
- Check if the armature is hidden in the Outliner

---

## Development Roadmap

### Phase 1: Foundation
- **1a:** Add-on registration ✅
- **1b:** Create puppet structure ✅
- **1c:** Body part selector UI + "Draw This View" button
- **1d:** Visual feedback (drawn/undrawn indicators)

### Phase 1.5: Body Proportions
- Proportion sliders (head size, limb length, etc.)
- Presets (Chibi, Heroic, Lanky, etc.)
- Lock proportions after drawing begins

### Phase 2: Drivers
- Rotation swap drivers (layer visibility based on angle)
- Shape key drivers (mouth, eyes, eyebrows)
- Test controls panel (manual sliders)

### Phase 3: OSC Input
- OSC receiver for real-time tracking data
- Face tracking (MediaPipe/ARKit)
- Body tracking (MediaPipe Pose)
- Hand tracking (MediaPipe Hands)

### Phase 4: Recording
- Record performances to keyframes
- Playback and re-recording
- Export standard Blender animation

---

## Inspiration

- [Adobe Character Animator](https://www.adobe.com/products/character-animator.html)
- [Duik Ángela](https://rxlaboratory.org/tools/duik-angela/) (After Effects rigging)
- [Blender Studio - Impulse Purchase](https://studio.blender.org/films/impulse-purchase/) (OK Go music video)

---

## License

MIT License — feel free to use, modify, and distribute.

---

## Contributing

This project is in early development. Feedback and contributions welcome!
