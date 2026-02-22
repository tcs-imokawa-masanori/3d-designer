"""
3D Printer Hub — Reference Sites, Material Database, Cost Calculator, Multi-Printer Support
Features NO other LEGO builder app has!
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json, math, time, uuid, random

router = APIRouter(prefix="/api/printers", tags=["printers"])

# ========== 3D PRINTER DATABASE ==========
PRINTER_DATABASE = {
    # --- Bambu Lab ---
    "bambu_a1_mini": {
        "brand": "Bambu Lab", "model": "A1 Mini", "price_usd": 299,
        "bed_size": [180, 180, 180], "nozzle": 0.4, "max_speed": 500,
        "heated_bed": True, "enclosure": False, "auto_level": True,
        "multi_color": True, "ams_compatible": True,
        "url": "https://bambulab.com/en/a1-mini",
        "image": "🖨️", "rating": 4.7,
        "best_for": "Beginners, small prints, LEGO bricks",
        "materials": ["PLA", "PETG", "TPU", "PVA"],
    },
    "bambu_a1": {
        "brand": "Bambu Lab", "model": "A1", "price_usd": 399,
        "bed_size": [256, 256, 256], "nozzle": 0.4, "max_speed": 500,
        "heated_bed": True, "enclosure": False, "auto_level": True,
        "multi_color": True, "ams_compatible": True,
        "url": "https://bambulab.com/en/a1",
        "image": "🖨️", "rating": 4.8,
        "best_for": "Best value, medium prints, LEGO sets",
        "materials": ["PLA", "PETG", "TPU", "PVA"],
    },
    "bambu_p1s": {
        "brand": "Bambu Lab", "model": "P1S", "price_usd": 699,
        "bed_size": [256, 256, 256], "nozzle": 0.4, "max_speed": 500,
        "heated_bed": True, "enclosure": True, "auto_level": True,
        "multi_color": True, "ams_compatible": True,
        "url": "https://bambulab.com/en/p1s",
        "image": "🖨️", "rating": 4.8,
        "best_for": "Enclosed printing, ABS/ASA, detailed LEGO",
        "materials": ["PLA", "PETG", "ABS", "ASA", "TPU", "PA", "PC"],
    },
    "bambu_x1c": {
        "brand": "Bambu Lab", "model": "X1 Carbon", "price_usd": 1199,
        "bed_size": [256, 256, 256], "nozzle": 0.4, "max_speed": 500,
        "heated_bed": True, "enclosure": True, "auto_level": True,
        "multi_color": True, "ams_compatible": True, "lidar": True,
        "url": "https://bambulab.com/en/x1-carbon",
        "image": "🖨️", "rating": 4.9,
        "best_for": "Pro quality, carbon fiber, engineering prints",
        "materials": ["PLA", "PETG", "ABS", "ASA", "TPU", "PA", "PC", "CF"],
    },
    # --- Prusa ---
    "prusa_mk4s": {
        "brand": "Prusa", "model": "MK4S", "price_usd": 799,
        "bed_size": [250, 210, 220], "nozzle": 0.4, "max_speed": 200,
        "heated_bed": True, "enclosure": False, "auto_level": True,
        "multi_color": True, "ams_compatible": False,
        "url": "https://www.prusa3d.com/product/original-prusa-mk4s/",
        "image": "🖨️", "rating": 4.7,
        "best_for": "Reliability, open source, community support",
        "materials": ["PLA", "PETG", "ABS", "ASA", "TPU", "PA"],
    },
    "prusa_xl": {
        "brand": "Prusa", "model": "XL", "price_usd": 1999,
        "bed_size": [360, 360, 360], "nozzle": 0.4, "max_speed": 200,
        "heated_bed": True, "enclosure": False, "auto_level": True,
        "multi_color": True, "tool_changer": True,
        "url": "https://www.prusa3d.com/product/original-prusa-xl/",
        "image": "🖨️", "rating": 4.6,
        "best_for": "Large prints, multi-material, tool changer",
        "materials": ["PLA", "PETG", "ABS", "ASA", "TPU", "PA", "PC"],
    },
    "prusa_core_one": {
        "brand": "Prusa", "model": "Core One", "price_usd": 599,
        "bed_size": [250, 220, 270], "nozzle": 0.4, "max_speed": 500,
        "heated_bed": True, "enclosure": True, "auto_level": True,
        "multi_color": False,
        "url": "https://www.prusa3d.com/product/prusa-core-one/",
        "image": "🖨️", "rating": 4.7,
        "best_for": "Enclosed CoreXY, fast prints",
        "materials": ["PLA", "PETG", "ABS", "ASA", "TPU"],
    },
    # --- Creality ---
    "creality_k1_max": {
        "brand": "Creality", "model": "K1 Max", "price_usd": 599,
        "bed_size": [300, 300, 300], "nozzle": 0.4, "max_speed": 600,
        "heated_bed": True, "enclosure": True, "auto_level": True,
        "multi_color": False,
        "url": "https://www.creality.com/products/creality-k1-max-3d-printer",
        "image": "🖨️", "rating": 4.5,
        "best_for": "Large volume, fast speed, budget friendly",
        "materials": ["PLA", "PETG", "ABS", "TPU"],
    },
    "creality_ender3_v3": {
        "brand": "Creality", "model": "Ender-3 V3", "price_usd": 199,
        "bed_size": [220, 220, 250], "nozzle": 0.4, "max_speed": 500,
        "heated_bed": True, "enclosure": False, "auto_level": True,
        "multi_color": False,
        "url": "https://www.creality.com/products/ender-3-v3-3d-printer",
        "image": "🖨️", "rating": 4.4,
        "best_for": "Budget entry, great community, modding",
        "materials": ["PLA", "PETG", "TPU"],
    },
    # --- Anycubic ---
    "anycubic_kobra3": {
        "brand": "Anycubic", "model": "Kobra 3", "price_usd": 399,
        "bed_size": [250, 250, 260], "nozzle": 0.4, "max_speed": 600,
        "heated_bed": True, "enclosure": False, "auto_level": True,
        "multi_color": True,
        "url": "https://www.anycubic.com/products/kobra-3",
        "image": "🖨️", "rating": 4.5,
        "best_for": "Multi-color on budget, fast printing",
        "materials": ["PLA", "PETG", "TPU", "ABS"],
    },
    # --- Elegoo ---
    "elegoo_neptune4_pro": {
        "brand": "Elegoo", "model": "Neptune 4 Pro", "price_usd": 259,
        "bed_size": [225, 225, 265], "nozzle": 0.4, "max_speed": 500,
        "heated_bed": True, "enclosure": False, "auto_level": True,
        "multi_color": False,
        "url": "https://www.elegoo.com/products/elegoo-neptune-4-pro",
        "image": "🖨️", "rating": 4.4,
        "best_for": "Budget speed printer, great Klipper firmware",
        "materials": ["PLA", "PETG", "TPU", "ABS"],
    },
    # --- Resin Printers (for ultra-detail) ---
    "elegoo_saturn4_ultra": {
        "brand": "Elegoo", "model": "Saturn 4 Ultra", "price_usd": 399,
        "bed_size": [153, 77, 165], "nozzle": None, "max_speed": None,
        "type": "resin", "resolution_xy": 0.019,
        "heated_bed": False, "enclosure": True, "auto_level": True,
        "url": "https://www.elegoo.com/products/elegoo-saturn-4-ultra",
        "image": "🧪", "rating": 4.8,
        "best_for": "Ultra-detail, minifigures, jewelry, small LEGO parts",
        "materials": ["Standard Resin", "ABS-Like Resin", "Water Washable", "Tough Resin"],
    },
}

# ========== MATERIAL DATABASE ==========
MATERIALS = {
    "PLA": {
        "name": "PLA (Polylactic Acid)", "type": "filament",
        "temp_nozzle": [190, 220], "temp_bed": [50, 60],
        "price_per_kg": 20, "density": 1.24,
        "strength": "Medium", "flexibility": "Low", "detail": "High",
        "best_for": "LEGO bricks, figures, decorative items",
        "colors_available": 50, "biodegradable": True,
        "difficulty": "Easy", "odor": "None/Sweet",
        "icon": "🌽", "rating": 5,
        "print_speed": "Fast", "supports_needed": "Minimal",
        "lego_compatibility": "Excellent — closest to real LEGO feel",
    },
    "PLA+": {
        "name": "PLA+ (Enhanced PLA)", "type": "filament",
        "temp_nozzle": [200, 230], "temp_bed": [55, 65],
        "price_per_kg": 23, "density": 1.24,
        "strength": "Medium-High", "flexibility": "Low-Medium", "detail": "High",
        "best_for": "Stronger LEGO bricks, functional parts",
        "colors_available": 40, "difficulty": "Easy",
        "icon": "💪", "rating": 5,
        "lego_compatibility": "Best overall — stronger than PLA, same ease",
    },
    "PETG": {
        "name": "PETG (Polyethylene Terephthalate Glycol)", "type": "filament",
        "temp_nozzle": [220, 250], "temp_bed": [70, 85],
        "price_per_kg": 22, "density": 1.27,
        "strength": "High", "flexibility": "Medium", "detail": "Medium-High",
        "best_for": "Durable LEGO, outdoor use, water-resistant parts",
        "colors_available": 35, "difficulty": "Medium",
        "icon": "💎", "rating": 4,
        "lego_compatibility": "Good — slightly flexible, very durable",
    },
    "ABS": {
        "name": "ABS (Acrylonitrile Butadiene Styrene)", "type": "filament",
        "temp_nozzle": [230, 260], "temp_bed": [90, 110],
        "price_per_kg": 20, "density": 1.04,
        "strength": "High", "flexibility": "Medium", "detail": "Medium",
        "best_for": "Real LEGO material! Heat resistant, strong",
        "colors_available": 30, "difficulty": "Hard",
        "icon": "🧱", "rating": 4,
        "lego_compatibility": "Perfect — this IS what real LEGO uses!",
        "note": "Requires enclosure, emits fumes — ventilate well",
    },
    "ASA": {
        "name": "ASA (Acrylonitrile Styrene Acrylate)", "type": "filament",
        "temp_nozzle": [240, 260], "temp_bed": [90, 110],
        "price_per_kg": 25, "density": 1.07,
        "strength": "High", "flexibility": "Medium", "detail": "Medium",
        "best_for": "Outdoor LEGO displays, UV resistant",
        "colors_available": 20, "difficulty": "Hard",
        "icon": "☀️", "rating": 4,
        "lego_compatibility": "Excellent for outdoor — won't yellow",
    },
    "TPU": {
        "name": "TPU (Thermoplastic Polyurethane)", "type": "filament",
        "temp_nozzle": [220, 250], "temp_bed": [40, 60],
        "price_per_kg": 30, "density": 1.21,
        "strength": "High", "flexibility": "Very High", "detail": "Low",
        "best_for": "Flexible parts, tires, rubber-like LEGO",
        "colors_available": 15, "difficulty": "Hard",
        "icon": "🏐", "rating": 3,
        "lego_compatibility": "Good for tires & soft parts only",
    },
    "Nylon_PA": {
        "name": "Nylon/PA (Polyamide)", "type": "filament",
        "temp_nozzle": [240, 270], "temp_bed": [70, 90],
        "price_per_kg": 35, "density": 1.14,
        "strength": "Very High", "flexibility": "Medium", "detail": "Medium",
        "best_for": "Engineering LEGO, gears, Technic parts",
        "colors_available": 10, "difficulty": "Expert",
        "icon": "⚙️", "rating": 4,
        "lego_compatibility": "Best for Technic — extreme durability",
    },
    "PC": {
        "name": "Polycarbonate", "type": "filament",
        "temp_nozzle": [260, 310], "temp_bed": [100, 120],
        "price_per_kg": 40, "density": 1.20,
        "strength": "Extreme", "flexibility": "Low", "detail": "Medium",
        "best_for": "Industrial strength, transparent parts",
        "colors_available": 8, "difficulty": "Expert",
        "icon": "🔬", "rating": 3,
        "lego_compatibility": "Good for transparent/structural LEGO",
    },
    "CF_PLA": {
        "name": "Carbon Fiber PLA", "type": "filament",
        "temp_nozzle": [210, 240], "temp_bed": [55, 65],
        "price_per_kg": 35, "density": 1.3,
        "strength": "Very High", "flexibility": "Very Low", "detail": "High",
        "best_for": "Lightweight strong LEGO, matte finish",
        "colors_available": 5, "difficulty": "Medium",
        "icon": "🏎️", "rating": 4,
        "lego_compatibility": "Great — stiff, strong, premium look",
        "note": "Requires hardened steel nozzle",
    },
    "Resin_Standard": {
        "name": "Standard Resin", "type": "resin",
        "cure_time": 2.5, "price_per_kg": 30,
        "strength": "Medium", "flexibility": "Very Low", "detail": "Ultra High",
        "best_for": "Minifigures, tiny parts, jewelry",
        "icon": "🧪", "rating": 5,
        "lego_compatibility": "Best for micro/nano LEGO details",
    },
    "Resin_ABS_Like": {
        "name": "ABS-Like Resin", "type": "resin",
        "cure_time": 3.0, "price_per_kg": 35,
        "strength": "High", "flexibility": "Low", "detail": "Ultra High",
        "best_for": "Functional small parts, clips, connectors",
        "icon": "🧪", "rating": 4,
        "lego_compatibility": "Great for small functional LEGO parts",
    },
}

# ========== 3D PRINTING REFERENCE SITES ==========
REFERENCE_SITES = {
    "model_repositories": [
        {
            "name": "Thingiverse", "url": "https://www.thingiverse.com",
            "description": "Largest free 3D model library — millions of LEGO-compatible designs",
            "search_url": "https://www.thingiverse.com/search?q=lego",
            "lego_models": 50000, "free": True, "icon": "🌐",
        },
        {
            "name": "Printables (Prusa)", "url": "https://www.printables.com",
            "description": "Prusa's community — high quality, curated LEGO designs",
            "search_url": "https://www.printables.com/search/models?q=lego",
            "lego_models": 25000, "free": True, "icon": "🏆",
        },
        {
            "name": "MyMiniFactory", "url": "https://www.myminifactory.com",
            "description": "Premium quality models, many LEGO-compatible sets",
            "search_url": "https://www.myminifactory.com/search/?query=lego",
            "lego_models": 10000, "free": False, "icon": "💎",
        },
        {
            "name": "Thangs", "url": "https://thangs.com",
            "description": "AI-powered 3D model search — finds similar LEGO designs",
            "search_url": "https://thangs.com/search/lego",
            "lego_models": 30000, "free": True, "icon": "🤖",
        },
        {
            "name": "Cults3D", "url": "https://cults3d.com",
            "description": "Designer marketplace — unique LEGO-compatible creations",
            "search_url": "https://cults3d.com/en/search?q=lego",
            "lego_models": 15000, "free": False, "icon": "🎨",
        },
        {
            "name": "GrabCAD", "url": "https://grabcad.com",
            "description": "Engineering-focused — Technic and mechanical LEGO parts",
            "search_url": "https://grabcad.com/library?query=lego",
            "lego_models": 5000, "free": True, "icon": "⚙️",
        },
    ],
    "lego_specific": [
        {
            "name": "Rebrickable", "url": "https://rebrickable.com",
            "description": "Official LEGO part database — every brick ever made with dimensions",
            "icon": "🧱", "parts_count": 60000,
        },
        {
            "name": "BrickLink", "url": "https://www.bricklink.com",
            "description": "Buy/sell real LEGO parts — price reference for cost comparison",
            "icon": "💰", "parts_count": 100000,
        },
        {
            "name": "BrickOwl", "url": "https://www.brickowl.com",
            "description": "Alternative LEGO marketplace — compare prices",
            "icon": "🦉",
        },
        {
            "name": "LDraw.org", "url": "https://www.ldraw.org",
            "description": "Open standard for LEGO digital models — community-maintained part library",
            "icon": "📐", "parts_count": 15000,
        },
        {
            "name": "BrickLink Studio", "url": "https://www.bricklink.com/v3/studio/download.page",
            "description": "Free LEGO CAD software — import designs and order real parts",
            "icon": "🖥️",
        },
    ],
    "printer_resources": [
        {
            "name": "Bambu Lab", "url": "https://bambulab.com",
            "description": "Official Bambu Lab — printers, filament, accessories",
            "icon": "🖨️",
        },
        {
            "name": "Bambu Lab Wiki", "url": "https://wiki.bambulab.com",
            "description": "Official knowledge base — setup guides, troubleshooting",
            "icon": "📚",
        },
        {
            "name": "Prusa Knowledge Base", "url": "https://help.prusa3d.com",
            "description": "Prusa guides — calibration, materials, printing tips",
            "icon": "📚",
        },
        {
            "name": "All3DP", "url": "https://all3dp.com",
            "description": "3D printing news, reviews, best-of lists, buyer guides",
            "icon": "📰",
        },
        {
            "name": "3D Printing Industry", "url": "https://3dprintingindustry.com",
            "description": "Industry news, latest technology, product reviews",
            "icon": "📰",
        },
        {
            "name": "Tom's Hardware 3D Printing", "url": "https://www.tomshardware.com/3d-printing",
            "description": "In-depth reviews, benchmarks, buying guides",
            "icon": "📊",
        },
    ],
    "slicer_software": [
        {
            "name": "Bambu Studio", "url": "https://bambulab.com/en/download/studio",
            "description": "Bambu Lab's slicer — best for Bambu printers, supports 3MF",
            "free": True, "icon": "🔧",
        },
        {
            "name": "OrcaSlicer", "url": "https://github.com/SoftFever/OrcaSlicer",
            "description": "Open-source slicer — works with ALL printers, advanced features",
            "free": True, "icon": "🐋",
        },
        {
            "name": "PrusaSlicer", "url": "https://www.prusa3d.com/prusaslicer/",
            "description": "Prusa's slicer — excellent for Prusa and other printers",
            "free": True, "icon": "🔧",
        },
        {
            "name": "Cura", "url": "https://ultimaker.com/software/ultimaker-cura",
            "description": "Most popular slicer — huge plugin ecosystem",
            "free": True, "icon": "🔧",
        },
    ],
    "communities": [
        {
            "name": "r/3Dprinting", "url": "https://reddit.com/r/3Dprinting",
            "description": "Reddit's 3D printing community — 2M+ members",
            "members": 2000000, "icon": "👥",
        },
        {
            "name": "r/BambuLab", "url": "https://reddit.com/r/BambuLab",
            "description": "Bambu Lab owners community",
            "icon": "👥",
        },
        {
            "name": "r/lego", "url": "https://reddit.com/r/lego",
            "description": "LEGO community — inspiration for builds",
            "members": 1500000, "icon": "🧱",
        },
        {
            "name": "r/3DPrintedLego", "url": "https://reddit.com/r/3DPrintedLego",
            "description": "Dedicated to 3D printed LEGO — tips, designs, showcases",
            "icon": "🧱🖨️",
        },
    ],
}

# ========== LEGO DIMENSIONS DATABASE (for cost calculation) ==========
LEGO_REAL_PRICES = {
    "1x1": 0.05, "1x2": 0.06, "1x3": 0.07, "1x4": 0.08,
    "1x6": 0.10, "1x8": 0.12, "2x2": 0.08, "2x3": 0.10,
    "2x4": 0.12, "2x6": 0.15, "2x8": 0.18, "2x10": 0.22,
    "1x1_flat": 0.04, "1x2_flat": 0.05, "2x2_flat": 0.06, "2x4_flat": 0.08,
    "1x1_round": 0.06, "2x2_round": 0.10, "1x2_slope": 0.08, "2x2_slope": 0.10,
    "2x4_slope": 0.15, "1x1_cone": 0.07, "2x2_dome": 0.12,
}

# ========== BEST TIME TO BUY ==========
BEST_BUY_TIMES = {
    "bambu_lab": {
        "best_times": [
            {"event": "Black Friday / Cyber Monday", "month": "November", "discount": "15-25%", "icon": "🏷️"},
            {"event": "11.11 Singles Day", "month": "November 11", "discount": "10-20%", "icon": "🎉"},
            {"event": "Chinese New Year Sale", "month": "January/February", "discount": "10-15%", "icon": "🧧"},
            {"event": "Prime Day / Summer Sale", "month": "July", "discount": "10-15%", "icon": "☀️"},
            {"event": "New Model Launch", "month": "When new model releases", "discount": "Old models drop 10-20%", "icon": "🆕"},
        ],
        "current_tip": "Watch for Bambu Lab anniversary sales and bundle deals with AMS",
    },
    "prusa": {
        "best_times": [
            {"event": "Black Friday", "month": "November", "discount": "10-15%", "icon": "🏷️"},
            {"event": "Josef Prusa's Birthday", "month": "March", "discount": "5-10%", "icon": "🎂"},
            {"event": "Kit vs Assembled", "month": "Anytime", "discount": "Save $200+ with kit", "icon": "🔧"},
        ],
    },
    "creality": {
        "best_times": [
            {"event": "AliExpress Sales", "month": "3.28, 6.18, 11.11", "discount": "20-40%", "icon": "🏷️"},
            {"event": "Amazon Prime Day", "month": "July", "discount": "15-30%", "icon": "📦"},
            {"event": "Black Friday", "month": "November", "discount": "20-35%", "icon": "🏷️"},
        ],
    },
    "general_tips": [
        "🔍 Always check r/3Dprinting for deal alerts",
        "📊 Use CamelCamelCamel to track Amazon price history",
        "🏪 Check official stores vs Amazon — sometimes official is cheaper",
        "🎁 Bundle deals (printer + filament + accessories) save 20%+",
        "🔄 Refurbished/open box units save 15-30%",
        "⏰ Wait for new model announcements — old models drop in price",
    ],
}


# ========== API ENDPOINTS ==========

@router.get("/list")
async def list_printers():
    """Get all printers with comparison data"""
    printers = []
    for key, p in PRINTER_DATABASE.items():
        printers.append({
            "id": key,
            **p,
            "bed_volume_cm3": round(p["bed_size"][0] * p["bed_size"][1] * p["bed_size"][2] / 1000, 1) if p["bed_size"] else 0,
        })
    printers.sort(key=lambda x: x.get("price_usd", 0))
    return {"printers": printers, "count": len(printers)}


@router.get("/compare")
async def compare_printers(ids: str = "bambu_a1,bambu_p1s,prusa_mk4s"):
    """Compare specific printers side by side"""
    printer_ids = [p.strip() for p in ids.split(",")]
    comparison = []
    for pid in printer_ids:
        if pid in PRINTER_DATABASE:
            comparison.append({"id": pid, **PRINTER_DATABASE[pid]})
    return {"comparison": comparison}


@router.get("/recommend")
async def recommend_printer(budget: int = 500, use_case: str = "lego"):
    """Get printer recommendations based on budget and use case"""
    recommendations = []
    for key, p in PRINTER_DATABASE.items():
        if p.get("price_usd", 9999) <= budget:
            score = p.get("rating", 0) * 10
            if use_case == "lego":
                if p.get("multi_color"):
                    score += 15
                if p.get("enclosure"):
                    score += 5
                if "ABS" in p.get("materials", []):
                    score += 10
            elif use_case == "detail":
                if p.get("type") == "resin":
                    score += 20
            elif use_case == "large":
                vol = p["bed_size"][0] * p["bed_size"][1] * p["bed_size"][2]
                score += vol / 100000
            recommendations.append({
                "id": key, "score": round(score, 1),
                **p
            })
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return {
        "recommendations": recommendations[:5],
        "budget": budget,
        "use_case": use_case,
    }


@router.get("/materials")
async def get_materials():
    """Get all materials with details"""
    return {"materials": MATERIALS}


@router.get("/materials/recommend")
async def recommend_material(part_type: str = "brick", outdoor: bool = False, flexible: bool = False):
    """Recommend best material for a specific part type"""
    recommendations = []
    for key, m in MATERIALS.items():
        score = 0
        if part_type == "brick":
            if "LEGO" in m.get("best_for", "").lower() or "brick" in m.get("best_for", "").lower():
                score += 20
            if m.get("detail") in ["High", "Ultra High"]:
                score += 10
        elif part_type == "technic":
            if m.get("strength") in ["High", "Very High", "Extreme"]:
                score += 20
        elif part_type == "minifig":
            if m.get("detail") in ["Ultra High"]:
                score += 25
            if m.get("type") == "resin":
                score += 15

        if outdoor and "UV" in m.get("best_for", ""):
            score += 15
        if flexible and m.get("flexibility") in ["High", "Very High"]:
            score += 20

        if score > 0:
            recommendations.append({"id": key, "score": score, **m})

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return {"recommendations": recommendations[:5], "part_type": part_type}


@router.get("/references")
async def get_references():
    """Get all 3D printing reference sites"""
    return {"references": REFERENCE_SITES}


@router.get("/best-time-to-buy")
async def best_time_to_buy():
    """Get the best times to buy 3D printers"""
    return {"best_times": BEST_BUY_TIMES}


@router.post("/cost-calculator")
async def calculate_cost(request: Request):
    """Calculate cost: 3D printing vs buying real LEGO"""
    data = await request.json()
    bricks = data.get("bricks", [])
    material = data.get("material", "PLA")
    printer = data.get("printer", "bambu_a1")

    if not bricks:
        return JSONResponse({"error": "No bricks to calculate"}, status_code=400)

    # Calculate real LEGO cost
    lego_cost = 0
    for brick in bricks:
        brick_type = brick.get("type", "2x4")
        lego_cost += LEGO_REAL_PRICES.get(brick_type, 0.10)

    # Calculate 3D print cost
    mat = MATERIALS.get(material, MATERIALS["PLA"])
    material_price_per_g = mat.get("price_per_kg", 20) / 1000

    # Estimate weight (approximate)
    total_weight_g = len(bricks) * 2.5  # ~2.5g per average brick
    print_material_cost = total_weight_g * material_price_per_g

    # Electricity cost (~0.15 kWh per hour, $0.12/kWh)
    print_hours = max(0.5, len(bricks) * 0.25)  # ~15 min per brick
    electricity_cost = print_hours * 0.15 * 0.12

    # Total 3D print cost
    total_print_cost = print_material_cost + electricity_cost

    # Printer info
    printer_info = PRINTER_DATABASE.get(printer, {})
    printer_cost = printer_info.get("price_usd", 0)

    # Break-even analysis
    cost_per_brick_lego = lego_cost / max(len(bricks), 1)
    cost_per_brick_3d = total_print_cost / max(len(bricks), 1)
    savings_per_brick = cost_per_brick_lego - cost_per_brick_3d
    break_even_bricks = int(printer_cost / max(savings_per_brick, 0.01)) if savings_per_brick > 0 else float('inf')

    return {
        "cost_comparison": {
            "real_lego": {
                "total": round(lego_cost, 2),
                "per_brick": round(cost_per_brick_lego, 4),
                "source": "BrickLink average prices",
            },
            "3d_printed": {
                "material_cost": round(print_material_cost, 2),
                "electricity_cost": round(electricity_cost, 2),
                "total": round(total_print_cost, 2),
                "per_brick": round(cost_per_brick_3d, 4),
                "material": material,
                "weight_g": round(total_weight_g, 1),
                "print_time_hours": round(print_hours, 1),
            },
            "savings": {
                "per_design": round(lego_cost - total_print_cost, 2),
                "percentage": round((1 - total_print_cost / max(lego_cost, 0.01)) * 100, 1),
                "break_even_bricks": break_even_bricks,
                "break_even_designs": max(1, int(break_even_bricks / max(len(bricks), 1))),
            },
            "printer": {
                "model": printer_info.get("model", "Unknown"),
                "cost": printer_cost,
            },
        },
        "brick_count": len(bricks),
    }


@router.get("/lego-dimensions")
async def get_lego_dimensions():
    """Get real LEGO brick dimensions in mm for accurate 3D printing"""
    return {
        "standard_dimensions": {
            "unit_width_mm": 8.0,
            "unit_depth_mm": 8.0,
            "brick_height_mm": 9.6,
            "plate_height_mm": 3.2,
            "stud_diameter_mm": 4.8,
            "stud_height_mm": 1.7,
            "wall_thickness_mm": 1.5,
            "tube_outer_diameter_mm": 6.5,
            "tube_inner_diameter_mm": 4.8,
            "tolerance_mm": 0.1,
        },
        "print_tips": {
            "tolerance": "Add 0.1-0.2mm tolerance for 3D printed LEGO to ensure fit",
            "layer_height": "Use 0.12-0.16mm for smooth studs",
            "infill": "20% gyroid works great for bricks",
            "walls": "3-4 wall loops for strength",
            "supports": "Design bricks to print without supports",
            "orientation": "Print bricks upside down (studs facing bed) for best quality",
        },
        "reference": "Based on official LEGO measurements from patents and community research",
    }


@router.get("/filament-calculator")
async def filament_calculator(weight_g: float = 100, material: str = "PLA"):
    """Calculate how much filament you need and cost"""
    mat = MATERIALS.get(material, MATERIALS["PLA"])
    price_per_kg = mat.get("price_per_kg", 20)
    density = mat.get("density", 1.24)

    # Standard spool is 1kg
    cost = weight_g * (price_per_kg / 1000)
    spools_needed = math.ceil(weight_g / 1000)
    length_m = weight_g / (density * math.pi * (1.75/2)**2) / 100  # approximate for 1.75mm filament

    return {
        "material": material,
        "weight_g": weight_g,
        "cost_usd": round(cost, 2),
        "length_m": round(length_m, 1),
        "spools_needed": spools_needed,
        "spool_cost": price_per_kg,
        "density_g_cm3": density,
    }
