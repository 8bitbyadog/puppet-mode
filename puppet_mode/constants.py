# constants.py
# ============================================================================
# Central definition of all bone names, layer names, and rotation views.
# This file is the single source of truth for the puppet structure.
# ============================================================================

# ----------------------------------------------------------------------------
# ROTATION VIEWS
# These define the different angle views available for replacement animation.
# ----------------------------------------------------------------------------

# Standard 6-direction rotation views (for head, torso parts)
ROTATION_VIEWS_FULL = ["Front", "3Q_L", "3Q_R", "Side_L", "Side_R", "Back"]

# Simplified 2-direction views (for arms, legs)
ROTATION_VIEWS_SIMPLE = ["Front", "Side"]

# Hand pose names
HAND_POSES = ["Open", "Fist", "Point", "Relaxed", "Spread"]

# Hand rotation views (front/back only since poses handle most variation)
HAND_ROTATION_VIEWS = ["Front", "Back"]


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
# GREASE PENCIL LAYER STRUCTURE
# Defines all GP layers organized by body region.
# Format: { "group_name": ["layer_name", ...] }
# ----------------------------------------------------------------------------

GP_LAYER_STRUCTURE = {
    # Head with full rotation views
    "Head": [
        "Head_Front", "Head_3Q_L", "Head_3Q_R",
        "Head_Side_L", "Head_Side_R", "Head_Back"
    ],

    # Eyes - single layers, will use shape keys for animation
    "Eyes": ["Eye_L", "Eye_R"],

    # Eyebrows - single layers, will use shape keys
    "Eyebrows": ["Eyebrow_L", "Eyebrow_R"],

    # Mouth - single layer, will use shape keys for phonemes/expressions
    "Mouth": ["Mouth"],

    # Torso parts with full rotation views
    "Chest": [
        "Chest_Front", "Chest_3Q_L", "Chest_3Q_R",
        "Chest_Side_L", "Chest_Side_R", "Chest_Back"
    ],
    "Spine": [
        "Spine_Front", "Spine_3Q_L", "Spine_3Q_R",
        "Spine_Side_L", "Spine_Side_R", "Spine_Back"
    ],
    "Hips": [
        "Hips_Front", "Hips_3Q_L", "Hips_3Q_R",
        "Hips_Side_L", "Hips_Side_R", "Hips_Back"
    ],

    # Arms with simple rotation views
    "Arm_Upper_L": ["Arm_Upper_L_Front", "Arm_Upper_L_Side"],
    "Arm_Lower_L": ["Arm_Lower_L_Front", "Arm_Lower_L_Side"],
    "Arm_Upper_R": ["Arm_Upper_R_Front", "Arm_Upper_R_Side"],
    "Arm_Lower_R": ["Arm_Lower_R_Front", "Arm_Lower_R_Side"],

    # Hands with pose + rotation combinations
    "Hand_L": [
        f"Hand_L_{pose}_{rot}"
        for pose in HAND_POSES
        for rot in HAND_ROTATION_VIEWS
    ],
    "Hand_R": [
        f"Hand_R_{pose}_{rot}"
        for pose in HAND_POSES
        for rot in HAND_ROTATION_VIEWS
    ],

    # Legs with simple rotation views
    "Leg_Upper_L": ["Leg_Upper_L_Front", "Leg_Upper_L_Side"],
    "Leg_Lower_L": ["Leg_Lower_L_Front", "Leg_Lower_L_Side"],
    "Leg_Upper_R": ["Leg_Upper_R_Front", "Leg_Upper_R_Side"],
    "Leg_Lower_R": ["Leg_Lower_R_Front", "Leg_Lower_R_Side"],

    # Feet with simple rotation views
    "Foot_L": ["Foot_L_Front", "Foot_L_Side"],
    "Foot_R": ["Foot_R_Front", "Foot_R_Side"],
}


# ----------------------------------------------------------------------------
# LAYER TO BONE MAPPING
# Maps each GP layer to its corresponding bone for parenting.
# ----------------------------------------------------------------------------

LAYER_TO_BONE = {
    # Head layers -> Head bone
    "Head_Front": "Head", "Head_3Q_L": "Head", "Head_3Q_R": "Head",
    "Head_Side_L": "Head", "Head_Side_R": "Head", "Head_Back": "Head",

    # Face layers -> respective bones
    "Eye_L": "Eye_L", "Eye_R": "Eye_R",
    "Eyebrow_L": "Eyebrow_L", "Eyebrow_R": "Eyebrow_R",
    "Mouth": "Jaw",

    # Torso layers
    "Chest_Front": "Chest", "Chest_3Q_L": "Chest", "Chest_3Q_R": "Chest",
    "Chest_Side_L": "Chest", "Chest_Side_R": "Chest", "Chest_Back": "Chest",
    "Spine_Front": "Spine", "Spine_3Q_L": "Spine", "Spine_3Q_R": "Spine",
    "Spine_Side_L": "Spine", "Spine_Side_R": "Spine", "Spine_Back": "Spine",
    "Hips_Front": "Hips", "Hips_3Q_L": "Hips", "Hips_3Q_R": "Hips",
    "Hips_Side_L": "Hips", "Hips_Side_R": "Hips", "Hips_Back": "Hips",

    # Arm layers
    "Arm_Upper_L_Front": "Arm_Upper_L", "Arm_Upper_L_Side": "Arm_Upper_L",
    "Arm_Lower_L_Front": "Arm_Lower_L", "Arm_Lower_L_Side": "Arm_Lower_L",
    "Arm_Upper_R_Front": "Arm_Upper_R", "Arm_Upper_R_Side": "Arm_Upper_R",
    "Arm_Lower_R_Front": "Arm_Lower_R", "Arm_Lower_R_Side": "Arm_Lower_R",

    # Hand layers (all poses map to Hand bone)
    **{f"Hand_L_{pose}_{rot}": "Hand_L" for pose in HAND_POSES for rot in HAND_ROTATION_VIEWS},
    **{f"Hand_R_{pose}_{rot}": "Hand_R" for pose in HAND_POSES for rot in HAND_ROTATION_VIEWS},

    # Leg layers
    "Leg_Upper_L_Front": "Leg_Upper_L", "Leg_Upper_L_Side": "Leg_Upper_L",
    "Leg_Lower_L_Front": "Leg_Lower_L", "Leg_Lower_L_Side": "Leg_Lower_L",
    "Leg_Upper_R_Front": "Leg_Upper_R", "Leg_Upper_R_Side": "Leg_Upper_R",
    "Leg_Lower_R_Front": "Leg_Lower_R", "Leg_Lower_R_Side": "Leg_Lower_R",

    # Foot layers
    "Foot_L_Front": "Foot_L", "Foot_L_Side": "Foot_L",
    "Foot_R_Front": "Foot_R", "Foot_R_Side": "Foot_R",
}


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
# UI ORGANIZATION
# Defines how body parts are grouped in the UI panel.
# ----------------------------------------------------------------------------

UI_BODY_REGIONS = {
    "Face": ["Head", "Eyes", "Eyebrows", "Mouth"],
    "Body": ["Chest", "Spine", "Hips", "Arm_Upper_L", "Arm_Lower_L",
             "Arm_Upper_R", "Arm_Lower_R", "Leg_Upper_L", "Leg_Lower_L",
             "Leg_Upper_R", "Leg_Lower_R", "Foot_L", "Foot_R"],
    "Hands": ["Hand_L", "Hand_R"],
}


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
