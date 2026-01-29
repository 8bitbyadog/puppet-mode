# constants.py
# ============================================================================
# Central definition of all bone names, layer names, and rotation views.
# This file is the single source of truth for the puppet structure.
#
# REDESIGNED: Simplified structure inspired by Adobe Character Animator.
# - View-based organization (Front, Quarter, Profile)
# - Fewer parts to draw (~25 vs 69)
# - All drawn parts stay visible as assembled character
# - Proper front-to-back layer ordering
# ============================================================================

# ----------------------------------------------------------------------------
# CHARACTER VIEWS
# Main view angles for the entire character (like Character Animator).
# Parts are drawn per-view rather than per-part-per-rotation.
# ----------------------------------------------------------------------------

# Primary views (most puppets need Front + one profile)
CHARACTER_VIEWS = ["Front", "Quarter_L", "Quarter_R", "Profile_L", "Profile_R"]

# Minimal views for quick puppets
MINIMAL_VIEWS = ["Front"]

# Full views including back (for turnaround)
FULL_VIEWS = ["Front", "Quarter_L", "Quarter_R", "Profile_L", "Profile_R", "Back"]

# Hand poses (optional, for expressive hands)
HAND_POSES = ["Open", "Fist", "Point"]

# Legacy compatibility - keep these for existing code
ROTATION_VIEWS_FULL = CHARACTER_VIEWS + ["Back"]
ROTATION_VIEWS_SIMPLE = ["Front", "Side"]
HAND_ROTATION_VIEWS = ["Palm", "Back"]


# ----------------------------------------------------------------------------
# BONE HIERARCHY
# Defines the complete armature structure as nested dictionaries.
# Format: { "bone_name": { "children": {...}, "head": (x,y,z), "tail": (x,y,z) } }
# Positions are relative, will be scaled by body type sliders.
# Y-axis is depth (front/back), Z-axis is up/down, X-axis is left/right.
# ----------------------------------------------------------------------------

# Default bone positions (normalized units, character facing -Y)
# These values create a roughly human-proportioned skeleton at ~2 units tall
BONE_HIERARCHY = {
    "Root": {
        "head": (0, 0, 0),
        "tail": (0, 0, 0.1),
        "children": {
            "Spine": {
                "head": (0, 0, 0.9),
                "tail": (0, 0, 1.1),
                "children": {
                    "Chest": {
                        "head": (0, 0, 1.1),
                        "tail": (0, 0, 1.4),
                        "children": {
                            "Neck": {
                                "head": (0, 0, 1.4),
                                "tail": (0, 0, 1.55),
                                "children": {
                                    "Head": {
                                        "head": (0, 0, 1.55),
                                        "tail": (0, 0, 1.85),
                                        "children": {
                                            "Eye_L": {
                                                "head": (0.06, -0.08, 1.75),
                                                "tail": (0.06, -0.12, 1.75),
                                                "children": {}
                                            },
                                            "Eye_R": {
                                                "head": (-0.06, -0.08, 1.75),
                                                "tail": (-0.06, -0.12, 1.75),
                                                "children": {}
                                            },
                                            "Eyebrow_L": {
                                                "head": (0.06, -0.08, 1.8),
                                                "tail": (0.06, -0.1, 1.8),
                                                "children": {}
                                            },
                                            "Eyebrow_R": {
                                                "head": (-0.06, -0.08, 1.8),
                                                "tail": (-0.06, -0.1, 1.8),
                                                "children": {}
                                            },
                                            "Jaw": {
                                                "head": (0, -0.05, 1.65),
                                                "tail": (0, -0.1, 1.6),
                                                "children": {}
                                            }
                                        }
                                    }
                                }
                            },
                            # Left arm - slight elbow bend for IK, palm facing down
                            "Shoulder_L": {
                                "head": (0.05, 0, 1.35),
                                "tail": (0.15, 0, 1.35),
                                "children": {
                                    "Arm_Upper_L": {
                                        "head": (0.15, 0, 1.35),
                                        "tail": (0.4, 0, 1.35),
                                        "children": {
                                            # Elbow has slight forward bend for IK pole targeting
                                            "Arm_Lower_L": {
                                                "head": (0.4, 0, 1.35),
                                                "tail": (0.62, -0.04, 1.32),  # Slight forward (-Y) and down (-Z) bend
                                                "children": {
                                                    # Hand with palm facing floor
                                                    "Hand_L": {
                                                        "head": (0.62, -0.04, 1.32),
                                                        "tail": (0.72, -0.04, 1.32),
                                                        "children": {
                                                            # Thumb points FORWARD (-Y direction)
                                                            "Thumb_L_1": {
                                                                "head": (0.66, -0.06, 1.32),
                                                                "tail": (0.66, -0.10, 1.32),
                                                                "children": {
                                                                    "Thumb_L_2": {
                                                                        "head": (0.66, -0.10, 1.32),
                                                                        "tail": (0.66, -0.13, 1.32),
                                                                        "children": {
                                                                            "Thumb_L_3": {
                                                                                "head": (0.66, -0.13, 1.32),
                                                                                "tail": (0.66, -0.15, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Fingers spread HORIZONTALLY (along X), varied Y for fan spread
                                                            # Index - front of hand
                                                            "Index_L_1": {
                                                                "head": (0.72, -0.06, 1.32),
                                                                "tail": (0.76, -0.06, 1.32),
                                                                "children": {
                                                                    "Index_L_2": {
                                                                        "head": (0.76, -0.06, 1.32),
                                                                        "tail": (0.79, -0.06, 1.32),
                                                                        "children": {
                                                                            "Index_L_3": {
                                                                                "head": (0.79, -0.06, 1.32),
                                                                                "tail": (0.81, -0.06, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Middle - center, longest finger
                                                            "Middle_L_1": {
                                                                "head": (0.72, -0.04, 1.32),
                                                                "tail": (0.77, -0.04, 1.32),
                                                                "children": {
                                                                    "Middle_L_2": {
                                                                        "head": (0.77, -0.04, 1.32),
                                                                        "tail": (0.81, -0.04, 1.32),
                                                                        "children": {
                                                                            "Middle_L_3": {
                                                                                "head": (0.81, -0.04, 1.32),
                                                                                "tail": (0.84, -0.04, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Ring - back of center
                                                            "Ring_L_1": {
                                                                "head": (0.72, -0.02, 1.32),
                                                                "tail": (0.76, -0.02, 1.32),
                                                                "children": {
                                                                    "Ring_L_2": {
                                                                        "head": (0.76, -0.02, 1.32),
                                                                        "tail": (0.79, -0.02, 1.32),
                                                                        "children": {
                                                                            "Ring_L_3": {
                                                                                "head": (0.79, -0.02, 1.32),
                                                                                "tail": (0.81, -0.02, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Pinky - back of hand
                                                            "Pinky_L_1": {
                                                                "head": (0.72, 0, 1.32),
                                                                "tail": (0.75, 0, 1.32),
                                                                "children": {
                                                                    "Pinky_L_2": {
                                                                        "head": (0.75, 0, 1.32),
                                                                        "tail": (0.77, 0, 1.32),
                                                                        "children": {
                                                                            "Pinky_L_3": {
                                                                                "head": (0.77, 0, 1.32),
                                                                                "tail": (0.79, 0, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            # Right arm - mirrored from left, same elbow bend and palm-down orientation
                            "Shoulder_R": {
                                "head": (-0.05, 0, 1.35),
                                "tail": (-0.15, 0, 1.35),
                                "children": {
                                    "Arm_Upper_R": {
                                        "head": (-0.15, 0, 1.35),
                                        "tail": (-0.4, 0, 1.35),
                                        "children": {
                                            # Elbow has slight forward bend for IK pole targeting
                                            "Arm_Lower_R": {
                                                "head": (-0.4, 0, 1.35),
                                                "tail": (-0.62, -0.04, 1.32),  # Slight forward (-Y) and down (-Z) bend
                                                "children": {
                                                    # Hand with palm facing floor
                                                    "Hand_R": {
                                                        "head": (-0.62, -0.04, 1.32),
                                                        "tail": (-0.72, -0.04, 1.32),
                                                        "children": {
                                                            # Thumb points FORWARD (-Y direction)
                                                            "Thumb_R_1": {
                                                                "head": (-0.66, -0.06, 1.32),
                                                                "tail": (-0.66, -0.10, 1.32),
                                                                "children": {
                                                                    "Thumb_R_2": {
                                                                        "head": (-0.66, -0.10, 1.32),
                                                                        "tail": (-0.66, -0.13, 1.32),
                                                                        "children": {
                                                                            "Thumb_R_3": {
                                                                                "head": (-0.66, -0.13, 1.32),
                                                                                "tail": (-0.66, -0.15, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Fingers spread HORIZONTALLY (along -X), varied Y for fan spread
                                                            # Index - front of hand
                                                            "Index_R_1": {
                                                                "head": (-0.72, -0.06, 1.32),
                                                                "tail": (-0.76, -0.06, 1.32),
                                                                "children": {
                                                                    "Index_R_2": {
                                                                        "head": (-0.76, -0.06, 1.32),
                                                                        "tail": (-0.79, -0.06, 1.32),
                                                                        "children": {
                                                                            "Index_R_3": {
                                                                                "head": (-0.79, -0.06, 1.32),
                                                                                "tail": (-0.81, -0.06, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Middle - center, longest finger
                                                            "Middle_R_1": {
                                                                "head": (-0.72, -0.04, 1.32),
                                                                "tail": (-0.77, -0.04, 1.32),
                                                                "children": {
                                                                    "Middle_R_2": {
                                                                        "head": (-0.77, -0.04, 1.32),
                                                                        "tail": (-0.81, -0.04, 1.32),
                                                                        "children": {
                                                                            "Middle_R_3": {
                                                                                "head": (-0.81, -0.04, 1.32),
                                                                                "tail": (-0.84, -0.04, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Ring - back of center
                                                            "Ring_R_1": {
                                                                "head": (-0.72, -0.02, 1.32),
                                                                "tail": (-0.76, -0.02, 1.32),
                                                                "children": {
                                                                    "Ring_R_2": {
                                                                        "head": (-0.76, -0.02, 1.32),
                                                                        "tail": (-0.79, -0.02, 1.32),
                                                                        "children": {
                                                                            "Ring_R_3": {
                                                                                "head": (-0.79, -0.02, 1.32),
                                                                                "tail": (-0.81, -0.02, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            # Pinky - back of hand
                                                            "Pinky_R_1": {
                                                                "head": (-0.72, 0, 1.32),
                                                                "tail": (-0.75, 0, 1.32),
                                                                "children": {
                                                                    "Pinky_R_2": {
                                                                        "head": (-0.75, 0, 1.32),
                                                                        "tail": (-0.77, 0, 1.32),
                                                                        "children": {
                                                                            "Pinky_R_3": {
                                                                                "head": (-0.77, 0, 1.32),
                                                                                "tail": (-0.79, 0, 1.32),
                                                                                "children": {}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "Hips": {
                        "head": (0, 0, 0.9),
                        "tail": (0, 0, 0.85),
                        "children": {
                            # Left leg - slight forward bend at knee for IK pole targeting
                            "Leg_Upper_L": {
                                "head": (0.1, 0, 0.85),
                                "tail": (0.1, -0.02, 0.45),  # Slight forward tilt
                                "children": {
                                    # Knee bends backward (+Y) for proper IK pole direction
                                    "Leg_Lower_L": {
                                        "head": (0.1, -0.02, 0.45),
                                        "tail": (0.1, 0.03, 0.08),  # Slight backward bend
                                        "children": {
                                            "Foot_L": {
                                                "head": (0.1, 0.03, 0.08),
                                                "tail": (0.1, -0.10, 0.02),
                                                "children": {}
                                            }
                                        }
                                    }
                                }
                            },
                            # Right leg - mirrored knee bend
                            "Leg_Upper_R": {
                                "head": (-0.1, 0, 0.85),
                                "tail": (-0.1, -0.02, 0.45),  # Slight forward tilt
                                "children": {
                                    # Knee bends backward (+Y) for proper IK pole direction
                                    "Leg_Lower_R": {
                                        "head": (-0.1, -0.02, 0.45),
                                        "tail": (-0.1, 0.03, 0.08),  # Slight backward bend
                                        "children": {
                                            "Foot_R": {
                                                "head": (-0.1, 0.03, 0.08),
                                                "tail": (-0.1, -0.10, 0.02),
                                                "children": {}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


# ----------------------------------------------------------------------------
# GREASE PENCIL LAYER STRUCTURE (SIMPLIFIED)
# Organized by DRAWABLE PARTS with proper front-to-back ordering.
#
# Design principle: Draw whole body parts, not segments.
# - "Body" = entire torso (chest + spine + hips combined)
# - "Arm_L" = whole left arm (upper + lower combined)
# - Face elements are shared across all views
#
# Layer order matters for 2D: layers at TOP of list render IN FRONT.
# ----------------------------------------------------------------------------

# The simplified drawable parts (what the user actually draws)
DRAWABLE_PARTS = [
    # Face elements (always visible, shared across head views)
    "Face_Features",  # Eyes, eyebrows, nose as one layer
    "Mouth",          # Separate for lip sync

    # Head views
    "Head",

    # Body (torso as single piece)
    "Body",

    # Arms (whole arm, not segmented)
    "Arm_L",
    "Arm_R",

    # Hands (optional poses)
    "Hand_L",
    "Hand_R",

    # Legs (whole leg, not segmented)
    "Leg_L",
    "Leg_R",

    # Feet
    "Foot_L",
    "Foot_R",
]

# Parts that need view variants (drawn per-view)
VIEW_DEPENDENT_PARTS = ["Head", "Body", "Arm_L", "Arm_R", "Leg_L", "Leg_R"]

# Parts that are shared across views (drawn once)
VIEW_INDEPENDENT_PARTS = ["Face_Features", "Mouth", "Hand_L", "Hand_R", "Foot_L", "Foot_R"]

# Front-to-back render order (index 0 = frontmost)
# This determines which parts overlap which
LAYER_ORDER = [
    # Frontmost (drawn on top)
    "Face_Features",
    "Mouth",
    "Head",
    "Hand_L",
    "Hand_R",
    "Arm_L",  # Arms in front of body
    "Arm_R",
    "Body",
    "Foot_L",
    "Foot_R",
    "Leg_L",
    "Leg_R",
    # Backmost (drawn behind)
]

# Generate the actual layer names
def _generate_layer_structure():
    """Generate GP layer structure with view variants."""
    structure = {}

    # View-dependent parts get a layer per view
    for part in VIEW_DEPENDENT_PARTS:
        structure[part] = [f"{part}_{view}" for view in CHARACTER_VIEWS]

    # View-independent parts get a single layer
    for part in VIEW_INDEPENDENT_PARTS:
        if part.startswith("Hand_"):
            # Hands can have pose variants
            structure[part] = [f"{part}_{pose}" for pose in HAND_POSES]
        else:
            structure[part] = [part]

    return structure

GP_LAYER_STRUCTURE = _generate_layer_structure()

# Legacy structure for backward compatibility
GP_LAYER_STRUCTURE_LEGACY = {
    "Head": [f"Head_{v}" for v in CHARACTER_VIEWS],
    "Eyes": ["Eye_L", "Eye_R"],
    "Eyebrows": ["Eyebrow_L", "Eyebrow_R"],
    "Mouth": ["Mouth"],
    "Chest": [f"Chest_{v}" for v in CHARACTER_VIEWS],
    "Arm_Upper_L": ["Arm_Upper_L_Front", "Arm_Upper_L_Side"],
    "Arm_Lower_L": ["Arm_Lower_L_Front", "Arm_Lower_L_Side"],
    "Hand_L": [f"Hand_L_{pose}" for pose in HAND_POSES],
    "Arm_Upper_R": ["Arm_Upper_R_Front", "Arm_Upper_R_Side"],
    "Arm_Lower_R": ["Arm_Lower_R_Front", "Arm_Lower_R_Side"],
    "Hand_R": [f"Hand_R_{pose}" for pose in HAND_POSES],
    "Leg_Upper_L": ["Leg_Upper_L_Front", "Leg_Upper_L_Side"],
    "Leg_Lower_L": ["Leg_Lower_L_Front", "Leg_Lower_L_Side"],
    "Foot_L": ["Foot_L"],
    "Leg_Upper_R": ["Leg_Upper_R_Front", "Leg_Upper_R_Side"],
    "Leg_Lower_R": ["Leg_Lower_R_Front", "Leg_Lower_R_Side"],
    "Foot_R": ["Foot_R"],
}


# ----------------------------------------------------------------------------
# LAYER TO BONE MAPPING
# Maps each GP layer to its corresponding bone for parenting.
# Simplified to work with the new combined body parts.
# ----------------------------------------------------------------------------

def _generate_layer_to_bone():
    """Generate layer-to-bone mapping for all layers."""
    mapping = {}

    # Head layers -> Head bone
    for view in CHARACTER_VIEWS:
        mapping[f"Head_{view}"] = "Head"

    # Face layers -> Head bone (they move with the head)
    mapping["Face_Features"] = "Head"
    mapping["Mouth"] = "Jaw"

    # Body layers -> Chest bone (torso root)
    for view in CHARACTER_VIEWS:
        mapping[f"Body_{view}"] = "Chest"

    # Arm layers -> Shoulder bones (arms move from shoulder)
    for view in CHARACTER_VIEWS:
        mapping[f"Arm_L_{view}"] = "Shoulder_L"
        mapping[f"Arm_R_{view}"] = "Shoulder_R"

    # Hand layers -> Hand bones
    for pose in HAND_POSES:
        mapping[f"Hand_L_{pose}"] = "Hand_L"
        mapping[f"Hand_R_{pose}"] = "Hand_R"

    # Leg layers -> Hip bone (legs move from hip)
    for view in CHARACTER_VIEWS:
        mapping[f"Leg_L_{view}"] = "Hips"
        mapping[f"Leg_R_{view}"] = "Hips"

    # Foot layers -> Foot bones
    mapping["Foot_L"] = "Foot_L"
    mapping["Foot_R"] = "Foot_R"

    return mapping

LAYER_TO_BONE = _generate_layer_to_bone()


# ----------------------------------------------------------------------------
# SHAPE KEY DEFINITIONS
# Defines all shape keys for parts that morph rather than swap views.
# Format: { "category": ["shape_key_name", ...] }
# ----------------------------------------------------------------------------

SHAPE_KEYS = {
    "Mouth": [
        "Mouth_Open", "Mouth_Wide", "Mouth_Smile", "Mouth_Frown",
        # Phoneme shapes for lip sync
        "Mouth_Ah", "Mouth_Oh", "Mouth_Ee", "Mouth_Oo", "Mouth_Mm", "Mouth_Ff"
    ],
    "Eye_L": [
        "Blink_L", "Squint_L", "Wide_L",
        "Look_Up_L", "Look_Down_L", "Look_Left_L", "Look_Right_L"
    ],
    "Eye_R": [
        "Blink_R", "Squint_R", "Wide_R",
        "Look_Up_R", "Look_Down_R", "Look_Left_R", "Look_Right_R"
    ],
    "Eyebrow_L": ["Eyebrow_Raise_L", "Eyebrow_Furrow_L", "Eyebrow_Sad_L"],
    "Eyebrow_R": ["Eyebrow_Raise_R", "Eyebrow_Furrow_R", "Eyebrow_Sad_R"],
}


# ----------------------------------------------------------------------------
# UI ORGANIZATION (SIMPLIFIED)
# Defines how body parts are grouped in the UI panel.
# Much simpler than before - just the drawable parts.
# ----------------------------------------------------------------------------

UI_BODY_REGIONS = {
    "Face": ["Head", "Face_Features", "Mouth"],
    "Body": ["Body", "Arm_L", "Arm_R", "Leg_L", "Leg_R", "Foot_L", "Foot_R"],
    "Hands": ["Hand_L", "Hand_R"],
}

# Parts that should be in the mini-outliner
OUTLINER_PARTS = [
    ("Face_Features", "Face"),
    ("Mouth", "Mouth"),
    ("Head", "Head"),
    ("Body", "Body"),
    ("Arm_L", "Left Arm"),
    ("Arm_R", "Right Arm"),
    ("Hand_L", "Left Hand"),
    ("Hand_R", "Right Hand"),
    ("Leg_L", "Left Leg"),
    ("Leg_R", "Right Leg"),
    ("Foot_L", "Left Foot"),
    ("Foot_R", "Right Foot"),
]


# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

def get_all_layer_names():
    """Return a flat list of all GP layer names."""
    layers = []
    for group_layers in GP_LAYER_STRUCTURE.values():
        layers.extend(group_layers)
    return layers


def get_total_drawable_parts():
    """Return the total count of drawable parts."""
    return len(get_all_layer_names())


def get_layers_for_part(part_name, view=None):
    """
    Get layer names for a given part.
    If view is specified, returns only that view's layer.
    """
    if part_name not in GP_LAYER_STRUCTURE:
        return []

    layers = GP_LAYER_STRUCTURE[part_name]

    if view and part_name in VIEW_DEPENDENT_PARTS:
        layer_name = f"{part_name}_{view}"
        return [layer_name] if layer_name in layers else []

    return layers


def get_layers_for_view(view):
    """Get all layers that should be visible for a given view."""
    layers = []

    for part in DRAWABLE_PARTS:
        if part in VIEW_DEPENDENT_PARTS:
            layers.append(f"{part}_{view}")
        elif part in VIEW_INDEPENDENT_PARTS:
            # Include all layers for view-independent parts
            layers.extend(GP_LAYER_STRUCTURE.get(part, []))

    return layers


def get_bone_names_flat():
    """Return a flat list of all bone names by traversing the hierarchy."""
    bones = []

    def traverse(node):
        for name, data in node.items():
            bones.append(name)
            if data.get("children"):
                traverse(data["children"])

    traverse(BONE_HIERARCHY)
    return bones


def get_layer_draw_order():
    """
    Return layers in proper draw order (back to front).
    Layers earlier in this list are rendered BEHIND layers later in the list.
    """
    ordered = []
    # Reverse LAYER_ORDER since GP renders bottom layers first
    for part in reversed(LAYER_ORDER):
        if part in GP_LAYER_STRUCTURE:
            ordered.extend(GP_LAYER_STRUCTURE[part])
    return ordered


def get_active_layers_for_view(view, hand_pose="Open"):
    """
    Get layer names that should be active for a specific view + hand pose.
    Returns exactly one layer per drawable part (the correct variant).

    Example for (Front, Open):
      Head_Front, Body_Front, Arm_L_Front, Arm_R_Front,
      Face_Features, Mouth, Hand_L_Open, Hand_R_Open,
      Leg_L_Front, Leg_R_Front, Foot_L, Foot_R
    """
    layers = []
    for part in DRAWABLE_PARTS:
        if part in VIEW_DEPENDENT_PARTS:
            layers.append(f"{part}_{view}")
        elif part.startswith("Hand_"):
            layers.append(f"{part}_{hand_pose}")
        else:
            layers.append(part)
    return layers


# ----------------------------------------------------------------------------
# PER-OBJECT GP HELPERS
# Used by the per-object architecture where each drawable part gets its own
# Grease Pencil object instead of sharing layers in one GP object.
# ----------------------------------------------------------------------------

def get_gp_object_name(puppet_name, layer_name):
    """
    Get the GP object name for a specific drawable layer.
    Each body part / view combination gets its own GP object.
    E.g., ("Puppet", "Head_Front") -> "Puppet_Head_Front"
    """
    return f"{puppet_name}_{layer_name}"


def _get_base_part_from_layer(layer_name):
    """
    Extract the base drawable part from a full layer name.
    E.g., "Head_Front" -> "Head", "Hand_L_Open" -> "Hand_L",
          "Face_Features" -> "Face_Features"
    """
    if layer_name in DRAWABLE_PARTS:
        return layer_name
    for part in DRAWABLE_PARTS:
        if layer_name.startswith(part + "_"):
            return part
    return layer_name


def get_y_offset_for_layer(layer_name):
    """
    Get Y-axis offset for z-ordering in front orthographic view.
    More negative Y = closer to camera = rendered in front.
    Uses LAYER_ORDER to determine stacking order.
    """
    base_part = _get_base_part_from_layer(layer_name)
    if base_part in LAYER_ORDER:
        index = LAYER_ORDER.index(base_part)
    else:
        index = len(LAYER_ORDER)
    # Frontmost (index 0) gets most negative Y
    return -(len(LAYER_ORDER) - index) * 0.001
