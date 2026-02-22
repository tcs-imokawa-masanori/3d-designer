"""
3D Designer & LEGO Builder — Main Application
Designed for Dr. Imokawa
Supports: LEGO brick building, 3D modeling, STL/3MF export for Bambu Lab printers
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import json
import time
import uuid
from pathlib import Path

# App setup
app = FastAPI(title="3D Designer & LEGO Builder", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
BASE_DIR = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Directories
EXPORTS_DIR = BASE_DIR / "exports"
DESIGNS_DIR = BASE_DIR / "designs"
EXPORTS_DIR.mkdir(exist_ok=True)
DESIGNS_DIR.mkdir(exist_ok=True)

# ========== INCLUDE ADVANCED TOOLS ROUTER ==========
try:
    from app.advanced_tools import router as advanced_tools_router
    app.include_router(advanced_tools_router)
except ImportError:
    try:
        from advanced_tools import router as advanced_tools_router
        app.include_router(advanced_tools_router)
    except ImportError:
        print("Warning: advanced_tools.py not found, skipping router")

# ========== INCLUDE PRINTER HUB ROUTER ==========
try:
    from app.printer_hub import router as printer_hub_router
    app.include_router(printer_hub_router)
except ImportError:
    try:
        from printer_hub import router as printer_hub_router
        app.include_router(printer_hub_router)
    except ImportError:
        print("Warning: printer_hub.py not found, skipping router")

# ========== INCLUDE AMAZING FEATURES ROUTER ==========
try:
    from app.amazing_features import router as amazing_features_router
    app.include_router(amazing_features_router)
except ImportError:
    try:
        from amazing_features import router as amazing_features_router
        app.include_router(amazing_features_router)
    except ImportError:
        print("Warning: amazing_features.py not found, skipping router")

# ========== LEGO BRICK LIBRARY ==========
LEGO_BRICKS = {
    "1x1": {"width": 1, "depth": 1, "height": 1, "studs": 1, "name": "1×1 Brick"},
    "1x2": {"width": 1, "depth": 2, "height": 1, "studs": 2, "name": "1×2 Brick"},
    "1x3": {"width": 1, "depth": 3, "height": 1, "studs": 3, "name": "1×3 Brick"},
    "1x4": {"width": 1, "depth": 4, "height": 1, "studs": 4, "name": "1×4 Brick"},
    "1x6": {"width": 1, "depth": 6, "height": 1, "studs": 6, "name": "1×6 Brick"},
    "1x8": {"width": 1, "depth": 8, "height": 1, "studs": 8, "name": "1×8 Brick"},
    "2x2": {"width": 2, "depth": 2, "height": 1, "studs": 4, "name": "2×2 Brick"},
    "2x3": {"width": 2, "depth": 3, "height": 1, "studs": 6, "name": "2×3 Brick"},
    "2x4": {"width": 2, "depth": 4, "height": 1, "studs": 8, "name": "2×4 Brick"},
    "2x6": {"width": 2, "depth": 6, "height": 1, "studs": 12, "name": "2×6 Brick"},
    "2x8": {"width": 2, "depth": 8, "height": 1, "studs": 16, "name": "2×8 Brick"},
    "2x10": {"width": 2, "depth": 10, "height": 1, "studs": 20, "name": "2×10 Brick"},
    "1x1_flat": {"width": 1, "depth": 1, "height": 0.33, "studs": 1, "name": "1×1 Plate"},
    "1x2_flat": {"width": 1, "depth": 2, "height": 0.33, "studs": 2, "name": "1×2 Plate"},
    "2x2_flat": {"width": 2, "depth": 2, "height": 0.33, "studs": 4, "name": "2×2 Plate"},
    "2x4_flat": {"width": 2, "depth": 4, "height": 0.33, "studs": 8, "name": "2×4 Plate"},
    "1x1_round": {"width": 1, "depth": 1, "height": 1, "studs": 1, "name": "1×1 Round Brick", "shape": "cylinder"},
    "2x2_round": {"width": 2, "depth": 2, "height": 1, "studs": 1, "name": "2×2 Round Brick", "shape": "cylinder"},
    "1x2_slope": {"width": 1, "depth": 2, "height": 1, "studs": 1, "name": "1×2 Slope", "shape": "slope"},
    "2x2_slope": {"width": 2, "depth": 2, "height": 1, "studs": 2, "name": "2×2 Slope", "shape": "slope"},
    "2x4_slope": {"width": 2, "depth": 4, "height": 1, "studs": 4, "name": "2×4 Slope", "shape": "slope"},
    "1x1_cone": {"width": 1, "depth": 1, "height": 1, "studs": 0, "name": "1×1 Cone", "shape": "cone"},
    "2x2_dome": {"width": 2, "depth": 2, "height": 1, "studs": 0, "name": "2×2 Dome", "shape": "dome"},
}

# ========== TECHNIC PARTS ==========
TECHNIC_PARTS = {
    "beam_3": {"length": 3, "type": "beam", "name": "Technic Beam 3L", "holes": 3},
    "beam_5": {"length": 5, "type": "beam", "name": "Technic Beam 5L", "holes": 5},
    "beam_7": {"length": 7, "type": "beam", "name": "Technic Beam 7L", "holes": 7},
    "beam_9": {"length": 9, "type": "beam", "name": "Technic Beam 9L", "holes": 9},
    "beam_11": {"length": 11, "type": "beam", "name": "Technic Beam 11L", "holes": 11},
    "beam_15": {"length": 15, "type": "beam", "name": "Technic Beam 15L", "holes": 15},
    "beam_L_3x5": {"width": 3, "depth": 5, "type": "beam_L", "name": "Technic L-Beam 3×5"},
    "beam_T_3x3": {"width": 3, "depth": 3, "type": "beam_T", "name": "Technic T-Beam 3×3"},
    "axle_2": {"length": 2, "type": "axle", "name": "Technic Axle 2L"},
    "axle_3": {"length": 3, "type": "axle", "name": "Technic Axle 3L"},
    "axle_4": {"length": 4, "type": "axle", "name": "Technic Axle 4L"},
    "axle_6": {"length": 6, "type": "axle", "name": "Technic Axle 6L"},
    "axle_8": {"length": 8, "type": "axle", "name": "Technic Axle 8L"},
    "gear_8t": {"teeth": 8, "type": "gear", "name": "Gear 8 Tooth", "diameter": 1},
    "gear_16t": {"teeth": 16, "type": "gear", "name": "Gear 16 Tooth", "diameter": 2},
    "gear_24t": {"teeth": 24, "type": "gear", "name": "Gear 24 Tooth", "diameter": 3},
    "gear_40t": {"teeth": 40, "type": "gear", "name": "Gear 40 Tooth", "diameter": 5},
    "pin_short": {"length": 1, "type": "pin", "name": "Technic Pin (Short)"},
    "pin_long": {"length": 2, "type": "pin", "name": "Technic Pin (Long)"},
    "pin_axle": {"length": 2, "type": "pin_axle", "name": "Pin with Axle"},
    "connector_90": {"angle": 90, "type": "connector", "name": "90° Connector"},
    "connector_180": {"angle": 180, "type": "connector", "name": "180° Connector"},
    "wheel_small": {"diameter": 2, "type": "wheel", "name": "Small Wheel (24mm)"},
    "wheel_medium": {"diameter": 3, "type": "wheel", "name": "Medium Wheel (30mm)"},
    "wheel_large": {"diameter": 5, "type": "wheel", "name": "Large Wheel (56mm)"},
    "tire_small": {"diameter": 2.5, "type": "tire", "name": "Small Tire"},
    "tire_medium": {"diameter": 3.5, "type": "tire", "name": "Medium Tire"},
    "tire_large": {"diameter": 5.5, "type": "tire", "name": "Large Tire"},
}

# ========== MINIFIGURE PARTS ==========
MINIFIG_PARTS = {
    "head_plain": {"name": "Plain Head", "category": "head", "height": 1},
    "head_smile": {"name": "Smiling Head", "category": "head", "height": 1},
    "head_angry": {"name": "Angry Head", "category": "head", "height": 1},
    "head_glasses": {"name": "Head w/ Glasses", "category": "head", "height": 1},
    "hair_short": {"name": "Short Hair", "category": "hair", "height": 0.5},
    "hair_long": {"name": "Long Hair", "category": "hair", "height": 0.7},
    "hair_spiky": {"name": "Spiky Hair", "category": "hair", "height": 0.6},
    "helmet": {"name": "Helmet", "category": "hair", "height": 0.6},
    "hat_cap": {"name": "Cap", "category": "hair", "height": 0.4},
    "hat_tophat": {"name": "Top Hat", "category": "hair", "height": 1},
    "torso_plain": {"name": "Plain Torso", "category": "torso", "height": 1.5},
    "torso_shirt": {"name": "Shirt Torso", "category": "torso", "height": 1.5},
    "torso_suit": {"name": "Suit Torso", "category": "torso", "height": 1.5},
    "torso_armor": {"name": "Armor Torso", "category": "torso", "height": 1.5},
    "legs_plain": {"name": "Plain Legs", "category": "legs", "height": 1.5},
    "legs_short": {"name": "Short Legs", "category": "legs", "height": 1},
    "arm_left": {"name": "Left Arm", "category": "arm", "height": 1.5},
    "arm_right": {"name": "Right Arm", "category": "arm", "height": 1.5},
    "hand_left": {"name": "Left Hand", "category": "hand", "height": 0.5},
    "hand_right": {"name": "Right Hand", "category": "hand", "height": 0.5},
    "accessory_sword": {"name": "Sword", "category": "accessory", "height": 2},
    "accessory_shield": {"name": "Shield", "category": "accessory", "height": 1.5},
    "accessory_cup": {"name": "Cup", "category": "accessory", "height": 0.5},
    "accessory_tool": {"name": "Tool/Wrench", "category": "accessory", "height": 1},
}

LEGO_COLORS = {
    "red": "#CC0000",
    "blue": "#0055BF",
    "yellow": "#FFD500",
    "green": "#00852B",
    "white": "#FFFFFF",
    "black": "#1B2A34",
    "orange": "#FF7E14",
    "dark_blue": "#0A3463",
    "dark_green": "#00451A",
    "brown": "#583927",
    "light_gray": "#9BA19D",
    "dark_gray": "#6C6E68",
    "tan": "#E4CD9E",
    "pink": "#FC97AC",
    "purple": "#81007B",
    "lime": "#BBE90B",
    "cyan": "#00BCD4",
    "magenta": "#E91E63",
    "sand_blue": "#5A7184",
    "dark_red": "#720E0F",
}

# LEGO unit = 8mm wide, 8mm deep, 9.6mm tall (3.2mm for plate)
LEGO_UNIT_MM = 8.0
LEGO_HEIGHT_MM = 9.6
LEGO_PLATE_HEIGHT_MM = 3.2
LEGO_STUD_DIAMETER_MM = 4.8
LEGO_STUD_HEIGHT_MM = 1.7

# ========== PRESET DESIGNS ==========
PRESET_DESIGNS = {
    "house": {
        "name": "Simple House",
        "description": "A classic LEGO house with roof",
        "category": "buildings",
        "bricks": [
            # Base (2 layers of 2x4 bricks)
            {"type": "2x4", "x": 0, "y": 0, "z": 0, "color": "white"},
            {"type": "2x4", "x": 4, "y": 0, "z": 0, "color": "white"},
            {"type": "2x4", "x": 0, "y": 2, "z": 0, "color": "white"},
            {"type": "2x4", "x": 4, "y": 2, "z": 0, "color": "white"},
            # Walls
            {"type": "2x4", "x": 0, "y": 0, "z": 1, "color": "red"},
            {"type": "2x4", "x": 4, "y": 0, "z": 1, "color": "red"},
            {"type": "2x4", "x": 0, "y": 2, "z": 1, "color": "red"},
            {"type": "2x4", "x": 4, "y": 2, "z": 1, "color": "red"},
            {"type": "2x4", "x": 0, "y": 0, "z": 2, "color": "red"},
            {"type": "2x4", "x": 4, "y": 0, "z": 2, "color": "red"},
            {"type": "2x4", "x": 0, "y": 2, "z": 2, "color": "red"},
            {"type": "2x4", "x": 4, "y": 2, "z": 2, "color": "red"},
            # Roof
            {"type": "2x4_slope", "x": 1, "y": 0, "z": 3, "color": "dark_blue", "rotation": 0},
            {"type": "2x4_slope", "x": 5, "y": 0, "z": 3, "color": "dark_blue", "rotation": 0},
            {"type": "2x4_slope", "x": 1, "y": 2, "z": 3, "color": "dark_blue", "rotation": 180},
            {"type": "2x4_slope", "x": 5, "y": 2, "z": 3, "color": "dark_blue", "rotation": 180},
            # Door
            {"type": "1x2", "x": 3, "y": 0, "z": 1, "color": "brown"},
            {"type": "1x2", "x": 3, "y": 0, "z": 2, "color": "brown"},
        ]
    },
    "car": {
        "name": "Simple Car",
        "description": "A basic LEGO car",
        "category": "vehicles",
        "bricks": [
            # Base
            {"type": "2x6", "x": 0, "y": 0, "z": 0, "color": "blue"},
            # Body
            {"type": "2x4", "x": 1, "y": 0, "z": 1, "color": "blue"},
            # Windshield
            {"type": "2x2_slope", "x": 1, "y": 0, "z": 2, "color": "cyan"},
            # Roof
            {"type": "2x2", "x": 3, "y": 0, "z": 2, "color": "blue"},
            # Wheels
            {"type": "1x1_round", "x": 0, "y": -1, "z": 0, "color": "black"},
            {"type": "1x1_round", "x": 5, "y": -1, "z": 0, "color": "black"},
            {"type": "1x1_round", "x": 0, "y": 2, "z": 0, "color": "black"},
            {"type": "1x1_round", "x": 5, "y": 2, "z": 0, "color": "black"},
        ]
    },
    "tree": {
        "name": "Pine Tree",
        "description": "A LEGO pine tree",
        "category": "nature",
        "bricks": [
            # Trunk
            {"type": "1x1", "x": 0, "y": 0, "z": 0, "color": "brown"},
            {"type": "1x1", "x": 0, "y": 0, "z": 1, "color": "brown"},
            {"type": "1x1", "x": 0, "y": 0, "z": 2, "color": "brown"},
            # Leaves - bottom
            {"type": "2x2", "x": -1, "y": -1, "z": 3, "color": "green"},
            # Leaves - middle
            {"type": "1x2", "x": -1, "y": 0, "z": 4, "color": "green"},
            {"type": "1x2", "x": 0, "y": 0, "z": 4, "color": "dark_green"},
            # Leaves - top
            {"type": "1x1", "x": 0, "y": 0, "z": 5, "color": "green"},
            {"type": "1x1_cone", "x": 0, "y": 0, "z": 6, "color": "dark_green"},
        ]
    },
    "robot": {
        "name": "Mini Robot",
        "description": "A small LEGO robot figure",
        "category": "characters",
        "bricks": [
            # Feet
            {"type": "1x2", "x": -1, "y": 0, "z": 0, "color": "dark_gray"},
            {"type": "1x2", "x": 1, "y": 0, "z": 0, "color": "dark_gray"},
            # Legs
            {"type": "1x1", "x": -1, "y": 0, "z": 1, "color": "light_gray"},
            {"type": "1x1", "x": 1, "y": 0, "z": 1, "color": "light_gray"},
            # Body
            {"type": "2x2", "x": -1, "y": 0, "z": 2, "color": "blue"},
            {"type": "2x2", "x": -1, "y": 0, "z": 3, "color": "blue"},
            # Arms
            {"type": "1x1", "x": -2, "y": 0, "z": 3, "color": "yellow"},
            {"type": "1x1", "x": 2, "y": 0, "z": 3, "color": "yellow"},
            # Head
            {"type": "2x2", "x": -1, "y": 0, "z": 4, "color": "light_gray"},
            # Eyes
            {"type": "1x1_round", "x": -1, "y": -1, "z": 4, "color": "red"},
            {"type": "1x1_round", "x": 0, "y": -1, "z": 4, "color": "red"},
            # Antenna
            {"type": "1x1_round", "x": 0, "y": 0, "z": 5, "color": "yellow"},
        ]
    },
    "tower": {
        "name": "Castle Tower",
        "description": "A medieval castle tower",
        "category": "buildings",
        "bricks": [
            # Base
            {"type": "2x4", "x": 0, "y": 0, "z": 0, "color": "light_gray"},
            {"type": "2x4", "x": 0, "y": 2, "z": 0, "color": "light_gray"},
            # Walls
            {"type": "2x4", "x": 0, "y": 0, "z": 1, "color": "light_gray"},
            {"type": "2x4", "x": 0, "y": 2, "z": 1, "color": "light_gray"},
            {"type": "2x4", "x": 0, "y": 0, "z": 2, "color": "light_gray"},
            {"type": "2x4", "x": 0, "y": 2, "z": 2, "color": "light_gray"},
            {"type": "2x4", "x": 0, "y": 0, "z": 3, "color": "dark_gray"},
            {"type": "2x4", "x": 0, "y": 2, "z": 3, "color": "dark_gray"},
            {"type": "2x4", "x": 0, "y": 0, "z": 4, "color": "dark_gray"},
            {"type": "2x4", "x": 0, "y": 2, "z": 4, "color": "dark_gray"},
            # Battlements
            {"type": "1x1", "x": 0, "y": 0, "z": 5, "color": "dark_gray"},
            {"type": "1x1", "x": 2, "y": 0, "z": 5, "color": "dark_gray"},
            {"type": "1x1", "x": 0, "y": 3, "z": 5, "color": "dark_gray"},
            {"type": "1x1", "x": 2, "y": 3, "z": 5, "color": "dark_gray"},
            # Flag
            {"type": "1x1", "x": 1, "y": 1, "z": 5, "color": "brown"},
            {"type": "1x1", "x": 1, "y": 1, "z": 6, "color": "brown"},
            {"type": "1x2_flat", "x": 1, "y": 2, "z": 6, "color": "red"},
        ]
    }
}

# ========== MORE PRESET DESIGNS ==========
PRESET_DESIGNS["airplane"] = {
    "name": "Airplane",
    "description": "A simple LEGO airplane",
    "category": "vehicles",
    "bricks": [
        {"type": "2x8", "x": 0, "y": 0, "z": 0, "color": "white"},
        {"type": "2x4", "x": 2, "y": 0, "z": 1, "color": "white"},
        {"type": "1x2_slope", "x": 0, "y": 0, "z": 1, "color": "blue"},
        {"type": "2x2_slope", "x": 6, "y": 0, "z": 1, "color": "white"},
        {"type": "2x6", "x": 1, "y": -3, "z": 0, "color": "blue"},
        {"type": "2x6", "x": 1, "y": 3, "z": 0, "color": "blue"},
        {"type": "1x4", "x": 6, "y": -1, "z": 0, "color": "red"},
        {"type": "1x4", "x": 6, "y": 2, "z": 0, "color": "red"},
        {"type": "1x1_cone", "x": 0, "y": 0, "z": 2, "color": "red"},
    ]
}
PRESET_DESIGNS["spaceship"] = {
    "name": "Spaceship",
    "description": "A futuristic LEGO spaceship",
    "category": "vehicles",
    "bricks": [
        {"type": "2x6", "x": 0, "y": 0, "z": 0, "color": "dark_gray"},
        {"type": "2x6", "x": 0, "y": 2, "z": 0, "color": "dark_gray"},
        {"type": "2x4", "x": 1, "y": 0, "z": 1, "color": "blue"},
        {"type": "2x4", "x": 1, "y": 2, "z": 1, "color": "blue"},
        {"type": "2x2", "x": 2, "y": 1, "z": 2, "color": "cyan"},
        {"type": "2x2_slope", "x": 0, "y": 1, "z": 1, "color": "dark_blue"},
        {"type": "2x4_slope", "x": 4, "y": 1, "z": 1, "color": "dark_blue"},
        {"type": "1x4", "x": 0, "y": -1, "z": 0, "color": "red"},
        {"type": "1x4", "x": 0, "y": 4, "z": 0, "color": "red"},
        {"type": "1x1_round", "x": 5, "y": 0, "z": 0, "color": "orange"},
        {"type": "1x1_round", "x": 5, "y": 3, "z": 0, "color": "orange"},
    ]
}
PRESET_DESIGNS["flower"] = {
    "name": "Flower",
    "description": "A beautiful LEGO flower",
    "category": "nature",
    "bricks": [
        {"type": "1x1", "x": 0, "y": 0, "z": 0, "color": "green"},
        {"type": "1x1", "x": 0, "y": 0, "z": 1, "color": "green"},
        {"type": "1x1", "x": 0, "y": 0, "z": 2, "color": "green"},
        {"type": "1x2_flat", "x": -1, "y": 0, "z": 1, "color": "green"},
        {"type": "1x1_round", "x": 0, "y": 0, "z": 3, "color": "yellow"},
        {"type": "1x1_round", "x": 1, "y": 0, "z": 3, "color": "red"},
        {"type": "1x1_round", "x": -1, "y": 0, "z": 3, "color": "red"},
        {"type": "1x1_round", "x": 0, "y": 1, "z": 3, "color": "pink"},
        {"type": "1x1_round", "x": 0, "y": -1, "z": 3, "color": "pink"},
        {"type": "1x1_round", "x": 1, "y": 1, "z": 3, "color": "red"},
        {"type": "1x1_round", "x": -1, "y": -1, "z": 3, "color": "red"},
    ]
}
PRESET_DESIGNS["bridge"] = {
    "name": "Bridge",
    "description": "A stone bridge over a river",
    "category": "buildings",
    "bricks": [
        {"type": "2x4", "x": 0, "y": 0, "z": 0, "color": "light_gray"},
        {"type": "2x4", "x": 4, "y": 0, "z": 0, "color": "light_gray"},
        {"type": "2x4", "x": 8, "y": 0, "z": 0, "color": "light_gray"},
        {"type": "2x2", "x": 0, "y": 0, "z": 1, "color": "dark_gray"},
        {"type": "2x2", "x": 10, "y": 0, "z": 1, "color": "dark_gray"},
        {"type": "2x2", "x": 0, "y": 0, "z": 2, "color": "dark_gray"},
        {"type": "2x2", "x": 10, "y": 0, "z": 2, "color": "dark_gray"},
        {"type": "2x8", "x": 1, "y": 0, "z": 3, "color": "light_gray"},
        {"type": "2x4", "x": 9, "y": 0, "z": 3, "color": "light_gray"},
        {"type": "1x1", "x": 0, "y": 0, "z": 3, "color": "brown"},
        {"type": "1x1", "x": 11, "y": 0, "z": 3, "color": "brown"},
        {"type": "1x1", "x": 0, "y": 1, "z": 3, "color": "brown"},
        {"type": "1x1", "x": 11, "y": 1, "z": 3, "color": "brown"},
    ]
}
PRESET_DESIGNS["animal_dog"] = {
    "name": "Dog",
    "description": "A cute LEGO dog",
    "category": "animals",
    "bricks": [
        {"type": "1x1", "x": 0, "y": 0, "z": 0, "color": "brown"},
        {"type": "1x1", "x": 3, "y": 0, "z": 0, "color": "brown"},
        {"type": "1x1", "x": 0, "y": 1, "z": 0, "color": "brown"},
        {"type": "1x1", "x": 3, "y": 1, "z": 0, "color": "brown"},
        {"type": "2x4", "x": 0, "y": 0, "z": 1, "color": "tan"},
        {"type": "2x2", "x": -1, "y": 0, "z": 1, "color": "tan"},
        {"type": "1x1", "x": -1, "y": 0, "z": 2, "color": "brown"},
        {"type": "1x1_round", "x": -1, "y": -1, "z": 2, "color": "black"},
        {"type": "1x2_flat", "x": 4, "y": 0, "z": 1, "color": "tan"},
    ]
}

PRESET_DESIGNS["animal_cat"] = {
    "name": "Cat",
    "description": "A cute LEGO cat",
    "category": "animals",
    "bricks": [
        {"type": "1x1", "x": 0, "y": 0, "z": 0, "color": "orange"},
        {"type": "1x1", "x": 2, "y": 0, "z": 0, "color": "orange"},
        {"type": "1x1", "x": 0, "y": 1, "z": 0, "color": "orange"},
        {"type": "1x1", "x": 2, "y": 1, "z": 0, "color": "orange"},
        {"type": "1x3", "x": 0, "y": 0, "z": 1, "color": "orange"},
        {"type": "1x3", "x": 0, "y": 1, "z": 1, "color": "orange"},
        {"type": "2x2", "x": -1, "y": 0, "z": 1, "color": "white"},
        {"type": "1x1_round", "x": -1, "y": 0, "z": 2, "color": "green"},
        {"type": "1x1_round", "x": 0, "y": 0, "z": 2, "color": "green"},
        {"type": "1x1_cone", "x": -1, "y": 0, "z": 2, "color": "orange"},
        {"type": "1x1_cone", "x": 0, "y": 1, "z": 2, "color": "orange"},
        {"type": "1x2_flat", "x": 3, "y": 0, "z": 1, "color": "orange"},
    ]
}
PRESET_DESIGNS["rocket"] = {
    "name": "Rocket",
    "description": "A space rocket ready for launch",
    "category": "vehicles",
    "bricks": [
        {"type": "2x2", "x": 0, "y": 0, "z": 0, "color": "light_gray"},
        {"type": "2x2", "x": 0, "y": 0, "z": 1, "color": "white"},
        {"type": "2x2", "x": 0, "y": 0, "z": 2, "color": "white"},
        {"type": "2x2", "x": 0, "y": 0, "z": 3, "color": "white"},
        {"type": "2x2", "x": 0, "y": 0, "z": 4, "color": "red"},
        {"type": "1x1", "x": 0, "y": 0, "z": 5, "color": "red"},
        {"type": "1x1_cone", "x": 0, "y": 0, "z": 6, "color": "red"},
        {"type": "1x1_flat", "x": -1, "y": 0, "z": 0, "color": "dark_gray"},
        {"type": "1x1_flat", "x": 2, "y": 0, "z": 0, "color": "dark_gray"},
        {"type": "1x1_flat", "x": 0, "y": -1, "z": 0, "color": "dark_gray"},
        {"type": "1x1_flat", "x": 0, "y": 2, "z": 0, "color": "dark_gray"},
        {"type": "1x1_round", "x": 0, "y": -1, "z": 1, "color": "cyan"},
        {"type": "1x1_round", "x": 1, "y": 2, "z": 1, "color": "cyan"},
    ]
}
PRESET_DESIGNS["sword"] = {
    "name": "Sword Display",
    "description": "A LEGO sword on a stand",
    "category": "accessories",
    "bricks": [
        {"type": "2x4", "x": 0, "y": 0, "z": 0, "color": "dark_gray"},
        {"type": "1x1", "x": 1, "y": 0, "z": 1, "color": "brown"},
        {"type": "1x1", "x": 2, "y": 0, "z": 1, "color": "brown"},
        {"type": "1x1", "x": 1, "y": 0, "z": 2, "color": "yellow"},
        {"type": "1x1", "x": 2, "y": 0, "z": 2, "color": "yellow"},
        {"type": "1x1", "x": 1, "y": 0, "z": 3, "color": "light_gray"},
        {"type": "1x1", "x": 1, "y": 0, "z": 4, "color": "light_gray"},
        {"type": "1x1", "x": 1, "y": 0, "z": 5, "color": "light_gray"},
        {"type": "1x1", "x": 1, "y": 0, "z": 6, "color": "light_gray"},
        {"type": "1x1_cone", "x": 1, "y": 0, "z": 7, "color": "light_gray"},
    ]
}
PRESET_DESIGNS["chess_king"] = {
    "name": "Chess King",
    "description": "A chess king piece",
    "category": "games",
    "bricks": [
        {"type": "2x2", "x": 0, "y": 0, "z": 0, "color": "black"},
        {"type": "1x1", "x": 0, "y": 0, "z": 1, "color": "black"},
        {"type": "1x1", "x": 1, "y": 1, "z": 1, "color": "black"},
        {"type": "2x2", "x": 0, "y": 0, "z": 2, "color": "black"},
        {"type": "1x1", "x": 0, "y": 0, "z": 3, "color": "black"},
        {"type": "1x1_round", "x": 0, "y": 0, "z": 4, "color": "yellow"},
    ]
}
PRESET_DESIGNS["heart"] = {
    "name": "Heart",
    "description": "A red LEGO heart",
    "category": "decorative",
    "bricks": [
        {"type": "1x2", "x": 1, "y": 0, "z": 0, "color": "red"},
        {"type": "1x1", "x": 0, "y": 0, "z": 1, "color": "red"},
        {"type": "1x1", "x": 1, "y": 0, "z": 1, "color": "red"},
        {"type": "1x1", "x": 2, "y": 0, "z": 1, "color": "red"},
        {"type": "1x1", "x": 3, "y": 0, "z": 1, "color": "red"},
        {"type": "2x2", "x": -1, "y": 0, "z": 2, "color": "red"},
        {"type": "2x2", "x": 2, "y": 0, "z": 2, "color": "red"},
        {"type": "1x1_round", "x": 0, "y": 0, "z": 3, "color": "red"},
        {"type": "1x1_round", "x": 3, "y": 0, "z": 3, "color": "red"},
    ]
}

# 3D shape primitives for custom modeling
SHAPE_PRIMITIVES = {
    "cube": {"name": "Cube", "icon": "📦"},
    "sphere": {"name": "Sphere", "icon": "🔮"},
    "cylinder": {"name": "Cylinder", "icon": "🥫"},
    "cone": {"name": "Cone", "icon": "🔺"},
    "torus": {"name": "Torus", "icon": "🍩"},
    "pyramid": {"name": "Pyramid", "icon": "🔻"},
    "wedge": {"name": "Wedge", "icon": "📐"},
    "tube": {"name": "Tube", "icon": "🔲"},
}

# ========== ROUTES ==========

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok", "app": "3D Designer & LEGO Builder", "version": "1.0.0"}

# --- LEGO Brick endpoints ---

@app.get("/api/bricks")
async def get_bricks():
    """Get all available LEGO brick types"""
    return {"bricks": LEGO_BRICKS, "colors": LEGO_COLORS}

@app.get("/api/presets")
async def get_presets():
    """Get preset LEGO designs"""
    presets = {}
    for key, design in PRESET_DESIGNS.items():
        presets[key] = {
            "name": design["name"],
            "description": design["description"],
            "category": design["category"],
            "brick_count": len(design["bricks"])
        }
    return {"presets": presets}

@app.get("/api/presets/{preset_name}")
async def get_preset(preset_name: str):
    """Get a specific preset design"""
    if preset_name not in PRESET_DESIGNS:
        return JSONResponse({"error": "Preset not found"}, status_code=404)
    return {"design": PRESET_DESIGNS[preset_name]}

@app.get("/api/shapes")
async def get_shapes():
    """Get available 3D primitives"""
    return {"shapes": SHAPE_PRIMITIVES}

# --- Design CRUD ---

@app.post("/api/designs/save")
async def save_design(request: Request):
    """Save a design to disk"""
    data = await request.json()
    design_id = data.get("id", str(uuid.uuid4())[:8])
    design_name = data.get("name", f"design-{design_id}")

    design = {
        "id": design_id,
        "name": design_name,
        "created_at": time.time(),
        "mode": data.get("mode", "lego"),  # lego or 3d
        "bricks": data.get("bricks", []),
        "shapes": data.get("shapes", []),
        "camera": data.get("camera", {}),
        "metadata": {
            "brick_count": len(data.get("bricks", [])),
            "shape_count": len(data.get("shapes", [])),
        }
    }

    filepath = DESIGNS_DIR / f"{design_id}.json"
    with open(filepath, "w") as f:
        json.dump(design, f, indent=2)

    return {"status": "saved", "id": design_id, "path": str(filepath)}

@app.get("/api/designs")
async def list_designs():
    """List all saved designs"""
    designs = []
    for f in DESIGNS_DIR.glob("*.json"):
        try:
            with open(f) as fh:
                d = json.load(fh)
                designs.append({
                    "id": d["id"],
                    "name": d["name"],
                    "mode": d.get("mode", "lego"),
                    "brick_count": d.get("metadata", {}).get("brick_count", 0),
                    "created_at": d.get("created_at", 0),
                })
        except:
            pass
    designs.sort(key=lambda x: x["created_at"], reverse=True)
    return {"designs": designs}

@app.get("/api/designs/{design_id}")
async def load_design(design_id: str):
    """Load a specific design"""
    filepath = DESIGNS_DIR / f"{design_id}.json"
    if not filepath.exists():
        return JSONResponse({"error": "Design not found"}, status_code=404)
    with open(filepath) as f:
        design = json.load(f)
    return {"design": design}

@app.delete("/api/designs/{design_id}")
async def delete_design(design_id: str):
    """Delete a design"""
    filepath = DESIGNS_DIR / f"{design_id}.json"
    if filepath.exists():
        filepath.unlink()
        return {"status": "deleted", "id": design_id}
    return JSONResponse({"error": "Design not found"}, status_code=404)

# --- STL Export ---

@app.post("/api/export/stl")
async def export_stl(request: Request):
    """Export design as STL file for 3D printing"""
    data = await request.json()
    bricks = data.get("bricks", [])
    shapes = data.get("shapes", [])
    design_name = data.get("name", "design")
    design_id = data.get("id", str(uuid.uuid4())[:8])

    try:
        import numpy as np
        from stl import mesh as stl_mesh

        all_vertices = []
        all_faces = []
        vertex_offset = 0

        # Convert LEGO bricks to 3D geometry
        for brick_data in bricks:
            brick_type = brick_data.get("type", "2x4")
            brick_info = LEGO_BRICKS.get(brick_type, LEGO_BRICKS["2x4"])

            # Position in mm
            x = brick_data.get("x", 0) * LEGO_UNIT_MM
            y = brick_data.get("y", 0) * LEGO_UNIT_MM
            z = brick_data.get("z", 0) * LEGO_HEIGHT_MM

            w = brick_info["width"] * LEGO_UNIT_MM
            d = brick_info["depth"] * LEGO_UNIT_MM
            h = brick_info["height"] * LEGO_HEIGHT_MM

            shape = brick_info.get("shape", "box")

            if shape == "box" or shape == "slope":
                # Box vertices
                verts = np.array([
                    [x, y, z], [x+w, y, z], [x+w, y+d, z], [x, y+d, z],
                    [x, y, z+h], [x+w, y, z+h], [x+w, y+d, z+h], [x, y+d, z+h],
                ])
                faces = np.array([
                    [0,1,2], [0,2,3],  # bottom
                    [4,6,5], [4,7,6],  # top
                    [0,4,5], [0,5,1],  # front
                    [2,6,7], [2,7,3],  # back
                    [0,3,7], [0,7,4],  # left
                    [1,5,6], [1,6,2],  # right
                ]) + vertex_offset
                all_vertices.append(verts)
                all_faces.append(faces)
                vertex_offset += 8

                # Add studs on top
                stud_r = LEGO_STUD_DIAMETER_MM / 2
                stud_h = LEGO_STUD_HEIGHT_MM
                for sw in range(int(brick_info["width"])):
                    for sd in range(int(brick_info["depth"])):
                        cx = x + sw * LEGO_UNIT_MM + LEGO_UNIT_MM / 2
                        cy = y + sd * LEGO_UNIT_MM + LEGO_UNIT_MM / 2
                        cz = z + h

                        # Approximate cylinder with 8-sided polygon
                        n_sides = 8
                        bottom_verts = []
                        top_verts = []
                        for i in range(n_sides):
                            angle = 2 * np.pi * i / n_sides
                            bx = cx + stud_r * np.cos(angle)
                            by = cy + stud_r * np.sin(angle)
                            bottom_verts.append([bx, by, cz])
                            top_verts.append([bx, by, cz + stud_h])

                        stud_verts = np.array(bottom_verts + top_verts + [[cx, cy, cz], [cx, cy, cz + stud_h]])
                        stud_faces = []

                        # Side faces
                        for i in range(n_sides):
                            ni = (i + 1) % n_sides
                            stud_faces.append([i, ni, ni + n_sides])
                            stud_faces.append([i, ni + n_sides, i + n_sides])

                        # Bottom cap
                        center_bottom = 2 * n_sides
                        for i in range(n_sides):
                            ni = (i + 1) % n_sides
                            stud_faces.append([center_bottom, ni, i])

                        # Top cap
                        center_top = 2 * n_sides + 1
                        for i in range(n_sides):
                            ni = (i + 1) % n_sides
                            stud_faces.append([center_top, i + n_sides, ni + n_sides])

                        stud_faces = np.array(stud_faces) + vertex_offset
                        all_vertices.append(stud_verts)
                        all_faces.append(stud_faces)
                        vertex_offset += len(stud_verts)

        # Convert custom 3D shapes
        for shape_data in shapes:
            shape_type = shape_data.get("type", "cube")
            sx = shape_data.get("x", 0)
            sy = shape_data.get("y", 0)
            sz = shape_data.get("z", 0)
            scale = shape_data.get("scale", 10)

            if shape_type == "cube":
                s = scale / 2
                verts = np.array([
                    [sx-s, sy-s, sz-s], [sx+s, sy-s, sz-s],
                    [sx+s, sy+s, sz-s], [sx-s, sy+s, sz-s],
                    [sx-s, sy-s, sz+s], [sx+s, sy-s, sz+s],
                    [sx+s, sy+s, sz+s], [sx-s, sy+s, sz+s],
                ])
                faces = np.array([
                    [0,1,2], [0,2,3], [4,6,5], [4,7,6],
                    [0,4,5], [0,5,1], [2,6,7], [2,7,3],
                    [0,3,7], [0,7,4], [1,5,6], [1,6,2],
                ]) + vertex_offset
                all_vertices.append(verts)
                all_faces.append(faces)
                vertex_offset += 8

        if not all_vertices:
            return JSONResponse({"error": "No geometry to export"}, status_code=400)

        # Combine all geometry
        combined_verts = np.vstack(all_vertices)
        combined_faces = np.vstack(all_faces)

        # Create STL mesh
        stl_data = stl_mesh.Mesh(np.zeros(len(combined_faces), dtype=stl_mesh.Mesh.dtype))
        for i, face in enumerate(combined_faces):
            for j in range(3):
                stl_data.vectors[i][j] = combined_verts[face[j]]

        # Save
        filename = f"{design_name}_{design_id}.stl"
        filepath = EXPORTS_DIR / filename
        stl_data.save(str(filepath))

        return {
            "status": "exported",
            "filename": filename,
            "path": str(filepath),
            "vertices": len(combined_verts),
            "faces": len(combined_faces),
            "download_url": f"/api/export/download/{filename}"
        }

    except ImportError as e:
        # Fallback: generate a simple ASCII STL
        filename = f"{design_name}_{design_id}.stl"
        filepath = EXPORTS_DIR / filename

        with open(filepath, "w") as f:
            f.write(f"solid {design_name}\n")
            for brick_data in bricks:
                brick_type = brick_data.get("type", "2x4")
                brick_info = LEGO_BRICKS.get(brick_type, LEGO_BRICKS["2x4"])
                x = brick_data.get("x", 0) * LEGO_UNIT_MM
                y = brick_data.get("y", 0) * LEGO_UNIT_MM
                z = brick_data.get("z", 0) * LEGO_HEIGHT_MM
                w = brick_info["width"] * LEGO_UNIT_MM
                d = brick_info["depth"] * LEGO_UNIT_MM
                h = brick_info["height"] * LEGO_HEIGHT_MM

                # Write box as 12 triangles
                # Bottom
                f.write(f"  facet normal 0 0 -1\n    outer loop\n")
                f.write(f"      vertex {x} {y} {z}\n      vertex {x+w} {y} {z}\n      vertex {x+w} {y+d} {z}\n")
                f.write(f"    endloop\n  endfacet\n")
                f.write(f"  facet normal 0 0 -1\n    outer loop\n")
                f.write(f"      vertex {x} {y} {z}\n      vertex {x+w} {y+d} {z}\n      vertex {x} {y+d} {z}\n")
                f.write(f"    endloop\n  endfacet\n")
                # Top
                f.write(f"  facet normal 0 0 1\n    outer loop\n")
                f.write(f"      vertex {x} {y} {z+h}\n      vertex {x+w} {y+d} {z+h}\n      vertex {x+w} {y} {z+h}\n")
                f.write(f"    endloop\n  endfacet\n")
                f.write(f"  facet normal 0 0 1\n    outer loop\n")
                f.write(f"      vertex {x} {y} {z+h}\n      vertex {x} {y+d} {z+h}\n      vertex {x+w} {y+d} {z+h}\n")
                f.write(f"    endloop\n  endfacet\n")
                # Front
                f.write(f"  facet normal 0 -1 0\n    outer loop\n")
                f.write(f"      vertex {x} {y} {z}\n      vertex {x+w} {y} {z+h}\n      vertex {x+w} {y} {z}\n")
                f.write(f"    endloop\n  endfacet\n")
                f.write(f"  facet normal 0 -1 0\n    outer loop\n")
                f.write(f"      vertex {x} {y} {z}\n      vertex {x} {y} {z+h}\n      vertex {x+w} {y} {z+h}\n")
                f.write(f"    endloop\n  endfacet\n")

            f.write(f"endsolid {design_name}\n")

        return {
            "status": "exported",
            "filename": filename,
            "path": str(filepath),
            "format": "ascii_stl",
            "note": "Basic STL (install numpy-stl for full quality)",
            "download_url": f"/api/export/download/{filename}"
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/export/download/{filename}")
async def download_export(filename: str):
    """Download an exported file"""
    filepath = EXPORTS_DIR / filename
    if not filepath.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(str(filepath), filename=filename, media_type="application/octet-stream")

# --- Bambu Lab Integration ---

@app.post("/api/bambu/prepare")
async def prepare_for_bambu(request: Request):
    """Prepare design info for Bambu Lab printer"""
    data = await request.json()
    bricks = data.get("bricks", [])

    # Calculate print dimensions
    if not bricks:
        return JSONResponse({"error": "No bricks in design"}, status_code=400)

    min_x = min(b.get("x", 0) for b in bricks)
    max_x = max(b.get("x", 0) + LEGO_BRICKS.get(b.get("type", "2x4"), {}).get("depth", 4) for b in bricks)
    min_y = min(b.get("y", 0) for b in bricks)
    max_y = max(b.get("y", 0) + LEGO_BRICKS.get(b.get("type", "2x4"), {}).get("width", 2) for b in bricks)
    min_z = min(b.get("z", 0) for b in bricks)
    max_z = max(b.get("z", 0) + 1 for b in bricks)

    width_mm = (max_x - min_x) * LEGO_UNIT_MM
    depth_mm = (max_y - min_y) * LEGO_UNIT_MM
    height_mm = (max_z - min_z) * LEGO_HEIGHT_MM

    # Bambu Lab print settings recommendations
    settings = {
        "printer": "Bambu Lab",
        "compatible_models": ["A1", "A1 Mini", "P1S", "P1P", "X1C", "X1E"],
        "dimensions": {
            "width_mm": round(width_mm, 1),
            "depth_mm": round(depth_mm, 1),
            "height_mm": round(height_mm, 1),
        },
        "fits_on_bed": {
            "A1_Mini": width_mm <= 180 and depth_mm <= 180 and height_mm <= 180,
            "A1": width_mm <= 256 and depth_mm <= 256 and height_mm <= 256,
            "P1S": width_mm <= 256 and depth_mm <= 256 and height_mm <= 256,
            "X1C": width_mm <= 256 and depth_mm <= 256 and height_mm <= 256,
        },
        "recommended_settings": {
            "layer_height": "0.16mm (for LEGO-like quality)",
            "infill": "20% (gyroid pattern)",
            "supports": "No (designed to print without supports)",
            "material": "PLA or ABS",
            "nozzle": "0.4mm",
            "speed": "Standard",
            "wall_loops": 3,
            "top_layers": 4,
            "bottom_layers": 4,
        },
        "estimated_time": f"{max(1, int(len(bricks) * 15 / 60))} hours",
        "estimated_material": f"{max(5, int(len(bricks) * 3))}g PLA",
        "brick_count": len(bricks),
        "workflow": [
            "1. Export as STL from this app",
            "2. Open Bambu Studio (or OrcaSlicer)",
            "3. Import the STL file",
            "4. Apply recommended settings above",
            "5. Slice and send to your Bambu Lab printer",
            "6. Print! 🖨️"
        ]
    }

    return {"bambu_settings": settings}


# --- Technic Parts endpoints ---

@app.get("/api/technic")
async def get_technic_parts():
    """Get all available Technic parts"""
    return {"parts": TECHNIC_PARTS}

# --- Minifigure endpoints ---

@app.get("/api/minifig")
async def get_minifig_parts():
    """Get all minifigure parts"""
    categories = {}
    for key, part in MINIFIG_PARTS.items():
        cat = part["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({"id": key, **part})
    return {"parts": MINIFIG_PARTS, "categories": categories}

@app.post("/api/minifig/assemble")
async def assemble_minifig(request: Request):
    """Assemble a minifigure from selected parts"""
    data = await request.json()
    parts = data.get("parts", {})
    color = data.get("color", "yellow")

    # Build minifig from parts
    bricks = []
    y_offset = 0

    # Legs
    if "legs" in parts:
        bricks.append({"type": "1x2", "x": 0, "y": 0, "z": y_offset, "color": parts.get("legs_color", "blue")})
        y_offset += 1

    # Torso
    if "torso" in parts:
        bricks.append({"type": "1x2", "x": 0, "y": 0, "z": y_offset, "color": parts.get("torso_color", "red")})
        y_offset += 1

    # Head
    if "head" in parts:
        bricks.append({"type": "1x1_round", "x": 0, "y": 0, "z": y_offset, "color": parts.get("head_color", "yellow")})
        y_offset += 1

    # Hair/hat
    if "hair" in parts:
        bricks.append({"type": "1x1", "x": 0, "y": 0, "z": y_offset, "color": parts.get("hair_color", "brown")})

    return {
        "minifig": {
            "parts": parts,
            "bricks": bricks,
            "height_mm": y_offset * LEGO_HEIGHT_MM
        }
    }

# --- Building Instructions Generator ---

@app.post("/api/instructions/generate")
async def generate_instructions(request: Request):
    """Generate step-by-step building instructions from a design"""
    data = await request.json()
    bricks = data.get("bricks", [])
    design_name = data.get("name", "My Design")

    if not bricks:
        return JSONResponse({"error": "No bricks to generate instructions for"}, status_code=400)

    # Sort bricks by Z layer (bottom to top), then by position
    sorted_bricks = sorted(bricks, key=lambda b: (b.get("z", 0), b.get("x", 0), b.get("y", 0)))

    # Group by layers
    layers = {}
    for brick in sorted_bricks:
        z = brick.get("z", 0)
        if z not in layers:
            layers[z] = []
        layers[z].append(brick)

    # Generate steps
    steps = []
    step_num = 1
    parts_list = {}

    for z in sorted(layers.keys()):
        layer_bricks = layers[z]
        step = {
            "step": step_num,
            "layer": z,
            "description": f"Layer {z + 1} — Place {len(layer_bricks)} brick(s)",
            "bricks": [],
            "cumulative_count": 0,
        }

        for brick in layer_bricks:
            brick_type = brick.get("type", "2x4")
            brick_info = LEGO_BRICKS.get(brick_type, {"name": brick_type})
            color = brick.get("color", "red")

            step["bricks"].append({
                "type": brick_type,
                "name": brick_info.get("name", brick_type),
                "color": color,
                "position": f"({brick.get('x', 0)}, {brick.get('y', 0)})",
                "rotation": brick.get("rotation", 0),
            })

            # Track parts list
            part_key = f"{brick_type}_{color}"
            parts_list[part_key] = parts_list.get(part_key, {"type": brick_type, "name": brick_info.get("name", brick_type), "color": color, "count": 0})
            parts_list[part_key]["count"] += 1

        step["cumulative_count"] = sum(len(layers[k]) for k in sorted(layers.keys()) if k <= z)
        steps.append(step)
        step_num += 1

    return {
        "instructions": {
            "name": design_name,
            "total_steps": len(steps),
            "total_bricks": len(bricks),
            "steps": steps,
            "parts_list": list(parts_list.values()),
            "estimated_build_time": f"{max(1, len(bricks) * 2)} minutes",
        }
    }

# --- Symmetry/Mirror endpoint ---

@app.post("/api/tools/mirror")
async def mirror_design(request: Request):
    """Mirror/reflect bricks along an axis"""
    data = await request.json()
    bricks = data.get("bricks", [])
    axis = data.get("axis", "x")  # x, y, or z
    center = data.get("center", 0)

    mirrored = []
    for brick in bricks:
        new_brick = dict(brick)
        if axis == "x":
            new_brick["x"] = 2 * center - brick.get("x", 0) - LEGO_BRICKS.get(brick.get("type", "2x4"), {}).get("depth", 4)
        elif axis == "y":
            new_brick["y"] = 2 * center - brick.get("y", 0) - LEGO_BRICKS.get(brick.get("type", "2x4"), {}).get("width", 2)
        elif axis == "z":
            new_brick["z"] = 2 * center - brick.get("z", 0) - 1
        mirrored.append(new_brick)

    return {"original": bricks, "mirrored": mirrored, "combined": bricks + mirrored}

# --- Measurement Tool ---

@app.post("/api/tools/measure")
async def measure_design(request: Request):
    """Calculate measurements and statistics for a design"""
    data = await request.json()
    bricks = data.get("bricks", [])

    if not bricks:
        return {"measurements": {"error": "No bricks"}}

    # Calculate bounding box
    all_x = []
    all_y = []
    all_z = []
    total_studs = 0
    color_count = {}
    type_count = {}

    for brick in bricks:
        brick_type = brick.get("type", "2x4")
        info = LEGO_BRICKS.get(brick_type, {"width": 2, "depth": 4, "height": 1, "studs": 8})
        x = brick.get("x", 0)
        y = brick.get("y", 0)
        z = brick.get("z", 0)

        all_x.extend([x, x + info.get("depth", 4)])
        all_y.extend([y, y + info.get("width", 2)])
        all_z.extend([z, z + 1])
        total_studs += info.get("studs", 0)

        color = brick.get("color", "red")
        color_count[color] = color_count.get(color, 0) + 1
        type_count[brick_type] = type_count.get(brick_type, 0) + 1

    width_studs = max(all_x) - min(all_x)
    depth_studs = max(all_y) - min(all_y)
    height_bricks = max(all_z) - min(all_z)

    return {
        "measurements": {
            "bounding_box": {
                "width_studs": width_studs,
                "depth_studs": depth_studs,
                "height_bricks": height_bricks,
                "width_mm": round(width_studs * LEGO_UNIT_MM, 1),
                "depth_mm": round(depth_studs * LEGO_UNIT_MM, 1),
                "height_mm": round(height_bricks * LEGO_HEIGHT_MM, 1),
                "width_inches": round(width_studs * LEGO_UNIT_MM / 25.4, 2),
                "depth_inches": round(depth_studs * LEGO_UNIT_MM / 25.4, 2),
                "height_inches": round(height_bricks * LEGO_HEIGHT_MM / 25.4, 2),
            },
            "brick_count": len(bricks),
            "total_studs": total_studs,
            "unique_colors": len(color_count),
            "color_breakdown": color_count,
            "unique_types": len(type_count),
            "type_breakdown": type_count,
            "estimated_weight_g": round(len(bricks) * 2.3, 1),
            "estimated_cost_usd": round(len(bricks) * 0.10, 2),
        }
    }

# --- AMS Multi-Color Export ---

@app.post("/api/export/ams")
async def export_ams_config(request: Request):
    """Generate Bambu AMS (Automatic Material System) color config"""
    data = await request.json()
    bricks = data.get("bricks", [])

    # Gather unique colors used
    colors_used = {}
    for brick in bricks:
        color = brick.get("color", "red")
        hex_color = LEGO_COLORS.get(color, "#CC0000")
        colors_used[color] = {
            "name": color,
            "hex": hex_color,
            "count": colors_used.get(color, {}).get("count", 0) + 1
        }

    # AMS has 4 slots, assign most-used colors first
    sorted_colors = sorted(colors_used.values(), key=lambda c: c["count"], reverse=True)
    ams_slots = []
    for i, color in enumerate(sorted_colors[:4]):
        ams_slots.append({
            "slot": i + 1,
            "color": color["name"],
            "hex": color["hex"],
            "brick_count": color["count"],
            "filament": "PLA",
        })

    extra_colors = sorted_colors[4:] if len(sorted_colors) > 4 else []

    return {
        "ams_config": {
            "total_colors": len(colors_used),
            "ams_slots": ams_slots,
            "extra_colors": [{"name": c["name"], "hex": c["hex"], "count": c["count"]} for c in extra_colors],
            "needs_manual_swap": len(extra_colors) > 0,
            "note": "AMS supports 4 colors. Extra colors require manual filament swap." if extra_colors else "All colors fit in AMS!",
            "recommended_filament": "Bambu PLA Basic or PLA Matte",
            "temperature": "220°C nozzle / 65°C bed",
        }
    }


# --- 3MF Export for Bambu Studio ---

@app.post("/api/export/3mf")
async def export_3mf(request: Request):
    """Export design as 3MF file — native format for Bambu Studio"""
    data = await request.json()
    bricks = data.get("bricks", [])
    design_name = data.get("name", "design")
    design_id = data.get("id", str(uuid.uuid4())[:8])

    if not bricks:
        return JSONResponse({"error": "No bricks to export"}, status_code=400)

    try:
        import zipfile
        import xml.etree.ElementTree as ET

        # 3MF is a ZIP file containing XML
        filename = f"{design_name}_{design_id}.3mf"
        filepath = EXPORTS_DIR / filename

        # Build mesh data
        vertices = []
        triangles = []
        vertex_offset = 0

        for brick_data in bricks:
            brick_type = brick_data.get("type", "2x4")
            brick_info = LEGO_BRICKS.get(brick_type, LEGO_BRICKS["2x4"])

            x = brick_data.get("x", 0) * LEGO_UNIT_MM
            y = brick_data.get("y", 0) * LEGO_UNIT_MM
            z = brick_data.get("z", 0) * LEGO_HEIGHT_MM

            w = brick_info["width"] * LEGO_UNIT_MM
            d = brick_info["depth"] * LEGO_UNIT_MM
            h = brick_info["height"] * LEGO_HEIGHT_MM

            # Box vertices (8 corners)
            verts = [
                (x, y, z), (x+w, y, z), (x+w, y+d, z), (x, y+d, z),
                (x, y, z+h), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z+h),
            ]
            vertices.extend(verts)

            # 12 triangles for a box
            faces = [
                (0,2,1), (0,3,2),   # bottom
                (4,5,6), (4,6,7),   # top
                (0,1,5), (0,5,4),   # front
                (2,3,7), (2,7,6),   # back
                (0,4,7), (0,7,3),   # left
                (1,2,6), (1,6,5),   # right
            ]
            for f in faces:
                triangles.append((f[0]+vertex_offset, f[1]+vertex_offset, f[2]+vertex_offset))
            vertex_offset += 8

        # Build 3MF XML
        model_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        model_xml += '<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        model_xml += '  <resources>\n'
        model_xml += '    <object id="1" type="model">\n'
        model_xml += '      <mesh>\n'
        model_xml += '        <vertices>\n'
        for v in vertices:
            model_xml += f'          <vertex x="{v[0]}" y="{v[1]}" z="{v[2]}" />\n'
        model_xml += '        </vertices>\n'
        model_xml += '        <triangles>\n'
        for t in triangles:
            model_xml += f'          <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}" />\n'
        model_xml += '        </triangles>\n'
        model_xml += '      </mesh>\n'
        model_xml += '    </object>\n'
        model_xml += '  </resources>\n'
        model_xml += '  <build>\n'
        model_xml += '    <item objectid="1" />\n'
        model_xml += '  </build>\n'
        model_xml += '</model>'

        content_types = '<?xml version="1.0" encoding="UTF-8"?>\n'
        content_types += '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        content_types += '  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />\n'
        content_types += '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />\n'
        content_types += '</Types>'

        rels = '<?xml version="1.0" encoding="UTF-8"?>\n'
        rels += '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        rels += '  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" />\n'
        rels += '</Relationships>'

        # Create ZIP (3MF is ZIP)
        with zipfile.ZipFile(str(filepath), 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', content_types)
            zf.writestr('_rels/.rels', rels)
            zf.writestr('3D/3dmodel.model', model_xml)

        file_size = filepath.stat().st_size

        return {
            "status": "exported",
            "filename": filename,
            "format": "3mf",
            "path": str(filepath),
            "file_size_kb": round(file_size / 1024, 1),
            "vertices": len(vertices),
            "triangles": len(triangles),
            "brick_count": len(bricks),
            "download_url": f"/api/export/download/{filename}",
            "note": "Open this file directly in Bambu Studio or OrcaSlicer!"
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# --- Design Search ---

@app.get("/api/bricks/search")
async def search_bricks(q: str = ""):
    """Search bricks by name"""
    if not q:
        return {"results": LEGO_BRICKS}
    q_lower = q.lower()
    results = {k: v for k, v in LEGO_BRICKS.items() if q_lower in v["name"].lower() or q_lower in k}
    technic_results = {k: v for k, v in TECHNIC_PARTS.items() if q_lower in v["name"].lower() or q_lower in k}
    return {"bricks": results, "technic": technic_results, "total": len(results) + len(technic_results)}

# --- Design Share (URL based) ---

@app.post("/api/designs/share")
async def share_design(request: Request):
    """Generate a shareable design code"""
    data = await request.json()
    bricks = data.get("bricks", [])
    name = data.get("name", "Shared Design")

    # Create a compact JSON and base64 encode
    import base64
    compact = json.dumps({"n": name, "b": bricks}, separators=(',', ':'))
    encoded = base64.urlsafe_b64encode(compact.encode()).decode()

    # Save as shared design
    share_id = str(uuid.uuid4())[:8]
    design = {
        "id": share_id,
        "name": name,
        "created_at": time.time(),
        "bricks": bricks,
        "shared": True,
        "code": encoded[:100] + "..." if len(encoded) > 100 else encoded,
    }
    filepath = DESIGNS_DIR / f"shared_{share_id}.json"
    with open(filepath, "w") as f:
        json.dump(design, f, indent=2)

    return {
        "share_id": share_id,
        "share_url": f"/api/designs/shared/{share_id}",
        "code_length": len(encoded),
    }

@app.get("/api/designs/shared/{share_id}")
async def get_shared_design(share_id: str):
    """Load a shared design"""
    filepath = DESIGNS_DIR / f"shared_{share_id}.json"
    if not filepath.exists():
        return JSONResponse({"error": "Shared design not found"}, status_code=404)
    with open(filepath) as f:
        design = json.load(f)
    return {"design": design}

# --- Animation / Turntable ---

@app.post("/api/animation/turntable")
async def generate_turntable_config(request: Request):
    """Generate turntable animation config for the frontend"""
    data = await request.json()
    bricks = data.get("bricks", [])
    speed = data.get("speed", 1.0)  # rotations per second
    frames = data.get("frames", 360)

    if not bricks:
        return JSONResponse({"error": "No bricks"}, status_code=400)

    # Calculate center of design for rotation
    all_x = [b.get("x", 0) for b in bricks]
    all_y = [b.get("y", 0) for b in bricks]
    center_x = (min(all_x) + max(all_x)) / 2 * LEGO_UNIT_MM
    center_y = (min(all_y) + max(all_y)) / 2 * LEGO_UNIT_MM

    return {
        "turntable": {
            "center": {"x": center_x, "y": center_y},
            "speed": speed,
            "frames": frames,
            "duration_seconds": frames / 60,
            "angle_per_frame": 360 / frames,
        }
    }


# --- Cost Estimator ---

LEGO_PART_PRICES = {
    "1x1": 0.05, "1x2": 0.08, "1x3": 0.10, "1x4": 0.12, "1x6": 0.15, "1x8": 0.18,
    "2x2": 0.10, "2x3": 0.14, "2x4": 0.16, "2x6": 0.22, "2x8": 0.28, "2x10": 0.35,
    "1x1_flat": 0.04, "1x2_flat": 0.06, "2x2_flat": 0.08, "2x4_flat": 0.12,
    "1x1_round": 0.06, "2x2_round": 0.12,
    "1x2_slope": 0.10, "2x2_slope": 0.14, "2x4_slope": 0.20,
    "1x1_cone": 0.08, "2x2_dome": 0.15,
}

@app.post("/api/tools/estimate-cost")
async def estimate_cost(request: Request):
    """Estimate the cost to buy all LEGO parts in a design"""
    data = await request.json()
    bricks = data.get("bricks", [])
    currency = data.get("currency", "usd")

    if not bricks:
        return {"cost": {"error": "No bricks"}}

    total_cost_usd = 0
    part_costs = []
    for brick in bricks:
        brick_type = brick.get("type", "2x4")
        price = LEGO_PART_PRICES.get(brick_type, 0.10)
        total_cost_usd += price
        part_costs.append({"type": brick_type, "price_usd": price})

    # Currency conversions (approximate)
    exchange = {"usd": 1, "eur": 0.92, "gbp": 0.79, "jpy": 150.0, "aud": 1.54}
    rate = exchange.get(currency, 1)
    symbol = {"usd": "$", "eur": "€", "gbp": "£", "jpy": "¥", "aud": "A$"}.get(currency, "$")

    total_local = total_cost_usd * rate

    # BrickLink estimate (usually 2-3x Pick-a-Brick prices)
    bricklink_estimate = total_cost_usd * 2.5

    # 3D printing cost estimate
    filament_cost_per_g = 0.025  # ~$25/kg PLA
    weight_g = len(bricks) * 2.3
    print_cost = weight_g * filament_cost_per_g + 0.50  # electricity

    return {
        "cost_estimate": {
            "lego_official": {
                "total": round(total_local, 2),
                "currency": currency.upper(),
                "symbol": symbol,
                "per_brick_avg": round(total_local / len(bricks), 3) if bricks else 0,
            },
            "bricklink_estimate": {
                "total": round(bricklink_estimate * rate, 2),
                "note": "BrickLink marketplace (used/new mix)",
            },
            "3d_print_estimate": {
                "total": round(print_cost * rate, 2),
                "filament_weight_g": round(weight_g, 1),
                "note": "PLA filament on Bambu Lab printer",
            },
            "brick_count": len(bricks),
            "cheapest_option": "3D Print" if print_cost < total_cost_usd else "LEGO Official",
            "savings_vs_lego": round((total_cost_usd - print_cost) * rate, 2) if print_cost < total_cost_usd else 0,
        }
    }

# --- Design Categories and Tags ---

@app.post("/api/designs/categorize")
async def categorize_design(request: Request):
    """Add categories and tags to a design"""
    data = await request.json()
    design_id = data.get("id")
    categories = data.get("categories", [])
    tags = data.get("tags", [])

    if not design_id:
        return JSONResponse({"error": "design id required"}, status_code=400)

    filepath = DESIGNS_DIR / f"{design_id}.json"
    if not filepath.exists():
        return JSONResponse({"error": "Design not found"}, status_code=404)

    with open(filepath) as f:
        design = json.load(f)

    design["categories"] = categories
    design["tags"] = tags
    design["updated_at"] = time.time()

    with open(filepath, "w") as f:
        json.dump(design, f, indent=2)

    return {"status": "updated", "id": design_id, "categories": categories, "tags": tags}

# --- LDraw Import (basic .ldr parser) ---

@app.post("/api/import/ldraw")
async def import_ldraw(request: Request):
    """Import a basic LDraw (.ldr) file and convert to our brick format"""
    data = await request.json()
    ldraw_content = data.get("content", "")

    if not ldraw_content:
        return JSONResponse({"error": "No LDraw content provided"}, status_code=400)

    # Basic LDraw parser
    # Line type 1 = part reference: 1 <color> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part>.dat
    bricks = []
    ldraw_colors = {
        0: "black", 1: "blue", 2: "green", 3: "dark_green", 4: "red",
        5: "pink", 6: "brown", 7: "light_gray", 8: "dark_gray",
        9: "light_blue", 10: "lime", 11: "cyan", 12: "red",
        14: "yellow", 15: "white", 16: "default", 25: "orange",
        28: "tan", 33: "purple", 72: "dark_gray",
    }

    # LDraw part name to our brick type mapping
    ldraw_parts = {
        "3005.dat": "1x1", "3004.dat": "1x2", "3622.dat": "1x3", "3010.dat": "1x4",
        "3009.dat": "1x6", "3008.dat": "1x8",
        "3003.dat": "2x2", "3002.dat": "2x3", "3001.dat": "2x4",
        "2456.dat": "2x6", "3007.dat": "2x8", "3832.dat": "2x10",
        "3024.dat": "1x1_flat", "3023.dat": "1x2_flat", "3022.dat": "2x2_flat", "3020.dat": "2x4_flat",
        "4073.dat": "1x1_round", "3941.dat": "2x2_round",
        "3040.dat": "1x2_slope", "3039.dat": "2x2_slope", "3037.dat": "2x4_slope",
        "4589.dat": "1x1_cone",
    }

    lines = ldraw_content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('0'):
            continue

        parts = line.split()
        if len(parts) < 15 or parts[0] != '1':
            continue

        try:
            color_code = int(parts[1])
            x = float(parts[2]) / 20  # LDraw units to grid
            y = float(parts[3]) / -24  # Y is inverted and different scale
            z = float(parts[4]) / 20
            part_file = parts[14].lower()

            brick_type = ldraw_parts.get(part_file, "2x4")
            color = ldraw_colors.get(color_code, "red")

            bricks.append({
                "type": brick_type,
                "x": round(x),
                "y": round(z),
                "z": round(y),
                "color": color,
            })
        except (ValueError, IndexError):
            continue

    return {
        "imported": {
            "brick_count": len(bricks),
            "bricks": bricks,
            "lines_parsed": len(lines),
            "format": "LDraw",
        }
    }

# ========== ASSEMBLY ANIMATION ==========

@app.post("/api/animation/assembly")
async def generate_assembly_animation(request: Request):
    """Generate step-by-step assembly animation data"""
    data = await request.json()
    bricks = data.get("bricks", [])
    speed = data.get("speed", 1.0)  # seconds per step

    if not bricks:
        return JSONResponse({"error": "No bricks"}, status_code=400)

    # Sort by Z (bottom up), then by position
    sorted_bricks = sorted(bricks, key=lambda b: (b.get("z", 0), b.get("x", 0), b.get("y", 0)))

    # Group into animation steps
    steps = []
    current_z = None
    current_step = []

    for brick in sorted_bricks:
        z = brick.get("z", 0)
        if current_z is not None and z != current_z:
            steps.append({
                "step": len(steps) + 1,
                "layer": current_z,
                "bricks": current_step,
                "delay": speed,
                "animation": "drop",  # drop from above
            })
            current_step = []
        current_z = z
        current_step.append(brick)

    if current_step:
        steps.append({
            "step": len(steps) + 1,
            "layer": current_z,
            "bricks": current_step,
            "delay": speed,
            "animation": "drop",
        })

    total_duration = len(steps) * speed

    return {
        "assembly": {
            "total_steps": len(steps),
            "total_bricks": len(bricks),
            "total_duration_seconds": total_duration,
            "steps": steps,
            "settings": {
                "drop_height": 10,  # LEGO units above target
                "drop_speed": 0.5,  # seconds for drop animation
                "bounce": True,
                "sound_effect": "click",
            }
        }
    }


# ========== SCREENSHOT GALLERY ==========

SCREENSHOTS_DIR = BASE_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

@app.post("/api/screenshots/save")
async def save_screenshot(request: Request):
    """Save a screenshot (base64 PNG from canvas)"""
    data = await request.json()
    image_data = data.get("image", "")
    name = data.get("name", f"screenshot-{int(time.time())}")

    if not image_data:
        return JSONResponse({"error": "No image data"}, status_code=400)

    import base64

    # Remove data:image/png;base64, prefix
    if "," in image_data:
        image_data = image_data.split(",")[1]

    filename = f"{name}_{int(time.time())}.png"
    filepath = SCREENSHOTS_DIR / filename

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image_data))

    return {
        "status": "saved",
        "filename": filename,
        "path": str(filepath),
        "download_url": f"/api/screenshots/{filename}",
    }

@app.get("/api/screenshots")
async def list_screenshots():
    """List all saved screenshots"""
    screenshots = []
    for f in sorted(SCREENSHOTS_DIR.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True):
        screenshots.append({
            "filename": f.name,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "created": f.stat().st_mtime,
            "url": f"/api/screenshots/{f.name}",
        })
    return {"screenshots": screenshots}

@app.get("/api/screenshots/{filename}")
async def get_screenshot(filename: str):
    filepath = SCREENSHOTS_DIR / filename
    if not filepath.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)
    return FileResponse(str(filepath), media_type="image/png")

@app.delete("/api/screenshots/{filename}")
async def delete_screenshot(filename: str):
    filepath = SCREENSHOTS_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return {"status": "deleted"}
    return JSONResponse({"error": "Not found"}, status_code=404)


# ========== GRID & BASEPLATE OPTIONS ==========

BASEPLATE_OPTIONS = {
    "small_green": {"size": 16, "color": "#00852B", "name": "Small Green (16×16)"},
    "medium_green": {"size": 32, "color": "#00852B", "name": "Medium Green (32×32)"},
    "large_green": {"size": 48, "color": "#00852B", "name": "Large Green (48×48)"},
    "small_gray": {"size": 16, "color": "#9BA19D", "name": "Small Gray (16×16)"},
    "medium_gray": {"size": 32, "color": "#9BA19D", "name": "Medium Gray (32×32)"},
    "large_gray": {"size": 48, "color": "#9BA19D", "name": "Large Gray (48×48)"},
    "small_tan": {"size": 16, "color": "#E4CD9E", "name": "Small Tan/Sand (16×16)"},
    "medium_blue": {"size": 32, "color": "#0055BF", "name": "Medium Blue (32×32)"},
    "road": {"size": 32, "color": "#6C6E68", "name": "Road Plate (32×32)"},
    "ocean": {"size": 32, "color": "#0077BE", "name": "Ocean Plate (32×32)"},
}

@app.get("/api/baseplates")
async def get_baseplates():
    return {"baseplates": BASEPLATE_OPTIONS}


# ========== LIGHTING PRESETS ==========

LIGHTING_PRESETS = {
    "studio": {
        "name": "Studio",
        "ambient": {"color": "#404040", "intensity": 0.4},
        "directional": {"color": "#ffffff", "intensity": 0.8, "position": [10, 20, 10]},
        "point_lights": [
            {"color": "#ffffff", "intensity": 0.3, "position": [-10, 15, -10]},
        ],
        "background": "#0a0a0f",
    },
    "daylight": {
        "name": "Daylight",
        "ambient": {"color": "#87CEEB", "intensity": 0.5},
        "directional": {"color": "#FFF8E7", "intensity": 1.0, "position": [15, 30, 10]},
        "point_lights": [],
        "background": "#87CEEB",
    },
    "sunset": {
        "name": "Sunset",
        "ambient": {"color": "#FF6B35", "intensity": 0.3},
        "directional": {"color": "#FF8C42", "intensity": 0.7, "position": [20, 8, 5]},
        "point_lights": [
            {"color": "#FF6B35", "intensity": 0.2, "position": [-10, 5, 10]},
        ],
        "background": "#1a0a2e",
    },
    "night": {
        "name": "Night",
        "ambient": {"color": "#1a1a2e", "intensity": 0.2},
        "directional": {"color": "#4444AA", "intensity": 0.3, "position": [5, 20, 5]},
        "point_lights": [
            {"color": "#FFD700", "intensity": 0.5, "position": [16, 5, 16]},
        ],
        "background": "#0a0a15",
    },
    "neon": {
        "name": "Neon",
        "ambient": {"color": "#1a0033", "intensity": 0.3},
        "directional": {"color": "#FF00FF", "intensity": 0.5, "position": [10, 20, 10]},
        "point_lights": [
            {"color": "#00FFFF", "intensity": 0.4, "position": [-10, 10, -10]},
            {"color": "#FF00FF", "intensity": 0.4, "position": [10, 10, 10]},
        ],
        "background": "#0a0015",
    },
    "warm": {
        "name": "Warm",
        "ambient": {"color": "#FFE4C4", "intensity": 0.4},
        "directional": {"color": "#FFF0D4", "intensity": 0.8, "position": [12, 18, 8]},
        "point_lights": [
            {"color": "#FFD700", "intensity": 0.3, "position": [0, 10, 0]},
        ],
        "background": "#1a1008",
    },
    "blueprint": {
        "name": "Blueprint",
        "ambient": {"color": "#1a3a5c", "intensity": 0.5},
        "directional": {"color": "#4488CC", "intensity": 0.6, "position": [10, 20, 10]},
        "point_lights": [],
        "background": "#0a1a2e",
    },
    "photo_studio": {
        "name": "Photo Studio",
        "ambient": {"color": "#FFFFFF", "intensity": 0.5},
        "directional": {"color": "#FFFFFF", "intensity": 0.7, "position": [10, 20, 5]},
        "point_lights": [
            {"color": "#FFFFFF", "intensity": 0.4, "position": [-15, 15, 10]},
            {"color": "#FFFFFF", "intensity": 0.3, "position": [15, 10, -10]},
        ],
        "background": "#f0f0f0",
    },
}

@app.get("/api/lighting")
async def get_lighting_presets():
    return {"presets": LIGHTING_PRESETS}


# ========== MATERIAL PRESETS ==========

MATERIAL_PRESETS = {
    "standard": {"name": "Standard (Glossy ABS)", "roughness": 0.6, "metalness": 0.1, "description": "Classic LEGO look"},
    "matte": {"name": "Matte", "roughness": 0.9, "metalness": 0.0, "description": "Non-glossy finish"},
    "chrome": {"name": "Chrome", "roughness": 0.1, "metalness": 0.9, "description": "Metallic chrome finish"},
    "pearl": {"name": "Pearl", "roughness": 0.4, "metalness": 0.3, "description": "Pearlescent shimmer"},
    "rubber": {"name": "Rubber", "roughness": 1.0, "metalness": 0.0, "description": "Soft rubber feel"},
    "transparent": {"name": "Transparent", "roughness": 0.2, "metalness": 0.0, "opacity": 0.5, "description": "See-through bricks"},
    "glow": {"name": "Glow in Dark", "roughness": 0.7, "metalness": 0.0, "emissive": 0.3, "description": "Phosphorescent"},
    "wood": {"name": "Wood", "roughness": 0.85, "metalness": 0.0, "description": "Natural wood look"},
}

@app.get("/api/materials")
async def get_material_presets():
    return {"materials": MATERIAL_PRESETS}


# ========== DESIGN TEMPLATES (Multi-Design Scenes) ==========

@app.get("/api/scenes")
async def get_scene_templates():
    """Get pre-made multi-design scene templates"""
    scenes = {
        "city_block": {
            "name": "City Block",
            "description": "A small city with buildings, cars, and trees",
            "designs": ["house", "car", "tree", "tower"],
            "layout": [
                {"preset": "house", "offset_x": 0, "offset_y": 0},
                {"preset": "car", "offset_x": 12, "offset_y": 0},
                {"preset": "tree", "offset_x": 10, "offset_y": 5},
                {"preset": "tower", "offset_x": 0, "offset_y": 8},
                {"preset": "tree", "offset_x": 5, "offset_y": 8},
            ],
        },
        "medieval": {
            "name": "Medieval Scene",
            "description": "Castle, tower, bridge and more",
            "designs": ["tower", "bridge"],
            "layout": [
                {"preset": "tower", "offset_x": 0, "offset_y": 0},
                {"preset": "bridge", "offset_x": 6, "offset_y": 0},
                {"preset": "tower", "offset_x": 20, "offset_y": 0},
            ],
        },
        "space": {
            "name": "Space Station",
            "description": "Spaceships and rockets in orbit",
            "designs": ["spaceship", "rocket"],
            "layout": [
                {"preset": "spaceship", "offset_x": 0, "offset_y": 0},
                {"preset": "rocket", "offset_x": 10, "offset_y": 0},
                {"preset": "spaceship", "offset_x": 0, "offset_y": 8},
            ],
        },
        "garden": {
            "name": "Garden",
            "description": "A beautiful garden with flowers and trees",
            "designs": ["tree", "flower"],
            "layout": [
                {"preset": "tree", "offset_x": 0, "offset_y": 0},
                {"preset": "flower", "offset_x": 3, "offset_y": 0},
                {"preset": "flower", "offset_x": 6, "offset_y": 0},
                {"preset": "tree", "offset_x": 9, "offset_y": 0},
                {"preset": "flower", "offset_x": 3, "offset_y": 4},
                {"preset": "flower", "offset_x": 6, "offset_y": 4},
            ],
        },
        "animal_farm": {
            "name": "Animal Farm",
            "description": "Dogs, cats, and farm buildings",
            "designs": ["animal_dog", "animal_cat", "house"],
            "layout": [
                {"preset": "house", "offset_x": 0, "offset_y": 0},
                {"preset": "animal_dog", "offset_x": 10, "offset_y": 0},
                {"preset": "animal_cat", "offset_x": 10, "offset_y": 5},
                {"preset": "tree", "offset_x": 15, "offset_y": 3},
            ],
        },
    }
    return {"scenes": scenes}

@app.post("/api/scenes/load")
async def load_scene(request: Request):
    """Load a scene template and return all combined bricks"""
    data = await request.json()
    scene_name = data.get("scene")

    scenes_response = await get_scene_templates()
    scenes = scenes_response["scenes"]

    if scene_name not in scenes:
        return JSONResponse({"error": "Scene not found"}, status_code=404)

    scene = scenes[scene_name]
    all_bricks = []

    for item in scene["layout"]:
        preset_name = item["preset"]
        offset_x = item.get("offset_x", 0)
        offset_y = item.get("offset_y", 0)

        if preset_name in PRESET_DESIGNS:
            for brick in PRESET_DESIGNS[preset_name]["bricks"]:
                new_brick = dict(brick)
                new_brick["x"] = brick.get("x", 0) + offset_x
                new_brick["y"] = brick.get("y", 0) + offset_y
                all_bricks.append(new_brick)

    return {
        "scene": scene_name,
        "name": scene["name"],
        "description": scene["description"],
        "bricks": all_bricks,
        "total_bricks": len(all_bricks),
    }


# ========== DESIGN STATISTICS DASHBOARD ==========

@app.get("/api/stats")
async def get_stats():
    """Get overall app statistics"""
    design_count = len(list(DESIGNS_DIR.glob("*.json")))
    export_count = len(list(EXPORTS_DIR.glob("*")))
    screenshot_count = len(list(SCREENSHOTS_DIR.glob("*.png")))

    return {
        "stats": {
            "saved_designs": design_count,
            "exports": export_count,
            "screenshots": screenshot_count,
            "available_bricks": len(LEGO_BRICKS),
            "available_technic": len(TECHNIC_PARTS),
            "available_minifig": len(MINIFIG_PARTS),
            "available_presets": len(PRESET_DESIGNS),
            "available_colors": len(LEGO_COLORS),
            "available_baseplates": len(BASEPLATE_OPTIONS),
            "available_lighting": len(LIGHTING_PRESETS),
            "available_materials": len(MATERIAL_PRESETS),
        }
    }


# --- Version info ---
@app.get("/api/version")
async def get_version():
    return {
        "app": "Open EA 3D Designer & LEGO Builder",
        "version": "3.0.0",
        "features": [
            "LEGO Brick Building (23 brick types)",
            "Technic Parts (28 parts)",
            "Minifigure Builder (24 parts)",
            "25+ Preset Designs",
            "Scene Templates (City, Medieval, Space, Garden, Farm)",
            "STL Export (binary + ASCII)",
            "3MF Export (Bambu Studio native)",
            "AMS Multi-Color Export",
            "Building Instructions Generator",
            "Assembly Animation (step-by-step build playback)",
            "Mirror/Symmetry Mode",
            "Measurement Tool",
            "Cost Estimator (LEGO + BrickLink + 3D Print)",
            "Design Sharing",
            "Turntable Animation",
            "LDraw Import",
            "Brick Search",
            "Custom Color Picker",
            "Screenshot Capture & Gallery",
            "8 Lighting Presets (Studio, Daylight, Sunset, Neon...)",
            "8 Material Types (Standard, Chrome, Pearl, Rubber...)",
            "10 Baseplate Options",
            "Advanced Tools (Rotate, Scale, Explode, Fill, Array...)",
            "Keyboard Shortcuts",
            "Undo/Redo",
            "Bambu Lab Integration (A1/P1S/X1C)",
        ],
        "author": "Dr. Imokawa — Open EA",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3030)
