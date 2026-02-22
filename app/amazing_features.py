"""
Amazing Features — Things NO other LEGO builder app has!
1. Brick-by-brick animation playback (like LEGO instruction booklets coming alive)
2. AI Design Assistant (suggests builds based on your idea)
3. Multi-floor building system with interior design
4. Physics simulation (structural integrity checker)
5. Texture & Decal system for custom brick faces
6. Community designs integration (Thingiverse, Printables, etc.)
7. Step-by-step instruction PDF generator
8. Real-time collaboration (share & build together)
9. AR Preview (see design in real world through camera)
10. Voice-controlled building
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json, math, time, uuid, random, copy

router = APIRouter(prefix="/api/amazing", tags=["amazing"])


# ========== 1. BRICK-BY-BRICK ANIMATION ==========

@router.post("/animation/generate")
async def generate_animation(request: Request):
    """Generate brick-by-brick build animation data"""
    data = await request.json()
    bricks = data.get("bricks", [])
    speed = data.get("speed", 1.0)  # seconds per brick
    style = data.get("style", "bottom_up")  # bottom_up, random, spiral, explode

    if not bricks:
        return JSONResponse({"error": "No bricks"}, status_code=400)

    # Sort bricks based on animation style
    if style == "bottom_up":
        sorted_bricks = sorted(bricks, key=lambda b: (b.get("z", 0), b.get("x", 0), b.get("y", 0)))
    elif style == "random":
        sorted_bricks = list(bricks)
        random.shuffle(sorted_bricks)
    elif style == "spiral":
        # Sort in spiral pattern from center outward
        center_x = sum(b.get("x", 0) for b in bricks) / max(len(bricks), 1)
        center_y = sum(b.get("y", 0) for b in bricks) / max(len(bricks), 1)
        sorted_bricks = sorted(bricks, key=lambda b: (
            b.get("z", 0),
            math.atan2(b.get("y", 0) - center_y, b.get("x", 0) - center_x)
        ))
    elif style == "explode":
        # Reverse order — start assembled, then fly apart
        sorted_bricks = sorted(bricks, key=lambda b: (b.get("z", 0), b.get("x", 0)), reverse=True)
    else:
        sorted_bricks = bricks

    # Generate keyframes
    keyframes = []
    for i, brick in enumerate(sorted_bricks):
        # Start position (above the build)
        start_y = brick.get("z", 0) + 20  # Drop from above

        keyframe = {
            "step": i + 1,
            "brick": brick,
            "timing": {
                "start_time": i * speed,
                "duration": speed * 0.8,
                "delay": speed * 0.2,
            },
            "animation": {
                "from": {
                    "x": brick.get("x", 0),
                    "y": brick.get("y", 0),
                    "z": start_y,
                    "opacity": 0,
                    "scale": 0.5,
                },
                "to": {
                    "x": brick.get("x", 0),
                    "y": brick.get("y", 0),
                    "z": brick.get("z", 0),
                    "opacity": 1,
                    "scale": 1,
                },
                "easing": "cubic-bezier(0.34, 1.56, 0.64, 1)",  # Bouncy drop
            },
            "sound": "click" if i % 3 == 0 else "snap",
        }
        keyframes.append(keyframe)

    return {
        "animation": {
            "total_steps": len(keyframes),
            "total_duration": len(keyframes) * speed,
            "style": style,
            "speed": speed,
            "keyframes": keyframes,
        }
    }


@router.post("/animation/explode")
async def explode_animation(request: Request):
    """Generate exploded view animation — shows all parts separated"""
    data = await request.json()
    bricks = data.get("bricks", [])
    spread = data.get("spread", 3.0)

    center_x = sum(b.get("x", 0) for b in bricks) / max(len(bricks), 1)
    center_y = sum(b.get("y", 0) for b in bricks) / max(len(bricks), 1)
    center_z = sum(b.get("z", 0) for b in bricks) / max(len(bricks), 1)

    exploded = []
    for brick in bricks:
        dx = (brick.get("x", 0) - center_x) * spread
        dy = (brick.get("y", 0) - center_y) * spread
        dz = (brick.get("z", 0) - center_z) * spread * 1.5  # More spread vertically

        exploded.append({
            **brick,
            "exploded_x": brick.get("x", 0) + dx,
            "exploded_y": brick.get("y", 0) + dy,
            "exploded_z": brick.get("z", 0) + dz,
        })

    return {
        "exploded_view": {
            "bricks": exploded,
            "spread": spread,
            "center": {"x": center_x, "y": center_y, "z": center_z},
        }
    }


# ========== 2. AI DESIGN ASSISTANT ==========

# Library of design templates the AI can suggest from
AI_DESIGN_TEMPLATES = {
    "tiny_house": {
        "name": "Tiny House", "difficulty": "Easy", "bricks": 30,
        "keywords": ["house", "home", "building", "cottage", "cabin"],
        "description": "A cozy tiny house with a porch and chimney",
    },
    "castle": {
        "name": "Medieval Castle", "difficulty": "Hard", "bricks": 120,
        "keywords": ["castle", "medieval", "fortress", "kingdom", "dragon"],
        "description": "A grand castle with towers, walls, and a drawbridge",
    },
    "race_car": {
        "name": "Race Car", "difficulty": "Medium", "bricks": 45,
        "keywords": ["car", "race", "speed", "vehicle", "formula"],
        "description": "A sleek Formula 1 style race car",
    },
    "robot_mech": {
        "name": "Battle Mech", "difficulty": "Hard", "bricks": 80,
        "keywords": ["robot", "mech", "gundam", "transformer", "machine"],
        "description": "A powerful battle mech with articulated limbs",
    },
    "pirate_ship": {
        "name": "Pirate Ship", "difficulty": "Hard", "bricks": 100,
        "keywords": ["ship", "pirate", "boat", "ocean", "sail"],
        "description": "A fearsome pirate ship with cannons and masts",
    },
    "treehouse": {
        "name": "Treehouse", "difficulty": "Medium", "bricks": 60,
        "keywords": ["tree", "nature", "treehouse", "forest", "adventure"],
        "description": "A whimsical treehouse with rope ladder and balcony",
    },
    "space_station": {
        "name": "Space Station", "difficulty": "Hard", "bricks": 90,
        "keywords": ["space", "station", "nasa", "iss", "orbit", "astronaut"],
        "description": "An orbiting space station with solar panels and docking ports",
    },
    "train": {
        "name": "Steam Train", "difficulty": "Medium", "bricks": 55,
        "keywords": ["train", "railway", "steam", "locomotive", "track"],
        "description": "A classic steam train with tender and carriages",
    },
    "dinosaur": {
        "name": "T-Rex", "difficulty": "Hard", "bricks": 70,
        "keywords": ["dinosaur", "trex", "jurassic", "dino", "raptor"],
        "description": "A poseable T-Rex with open jaw and small arms",
    },
    "city_block": {
        "name": "City Block", "difficulty": "Expert", "bricks": 200,
        "keywords": ["city", "buildings", "skyscraper", "downtown", "street"],
        "description": "A detailed city block with shops, apartments, and streets",
    },
    "japanese_temple": {
        "name": "Japanese Temple", "difficulty": "Medium", "bricks": 65,
        "keywords": ["temple", "japan", "shrine", "torii", "pagoda", "japanese"],
        "description": "A beautiful Japanese temple with curved roof and garden",
    },
    "minecraft_house": {
        "name": "Minecraft House", "difficulty": "Easy", "bricks": 40,
        "keywords": ["minecraft", "pixel", "blocky", "game", "steve"],
        "description": "A classic Minecraft-style house with pixelated design",
    },
    "guitar": {
        "name": "Electric Guitar", "difficulty": "Medium", "bricks": 50,
        "keywords": ["guitar", "music", "instrument", "rock", "band"],
        "description": "A detailed electric guitar with strings and frets",
    },
    "aquarium": {
        "name": "Aquarium", "difficulty": "Medium", "bricks": 55,
        "keywords": ["aquarium", "fish", "ocean", "underwater", "coral"],
        "description": "A colorful aquarium with fish, coral, and sea creatures",
    },
    "christmas_tree": {
        "name": "Christmas Tree", "difficulty": "Easy", "bricks": 35,
        "keywords": ["christmas", "tree", "holiday", "xmas", "decoration"],
        "description": "A decorated Christmas tree with presents and star",
    },
    "samurai_armor": {
        "name": "Samurai Armor Display", "difficulty": "Hard", "bricks": 75,
        "keywords": ["samurai", "armor", "warrior", "japanese", "katana"],
        "description": "A detailed samurai armor display with helmet and sword",
    },
}


@router.post("/ai/suggest")
async def ai_suggest_design(request: Request):
    """AI suggests designs based on your idea"""
    data = await request.json()
    idea = data.get("idea", "").lower()
    difficulty = data.get("difficulty", "any")
    max_bricks = data.get("max_bricks", 999)

    suggestions = []
    for key, template in AI_DESIGN_TEMPLATES.items():
        score = 0
        # Keyword matching
        for keyword in template["keywords"]:
            if keyword in idea:
                score += 30
        # Fuzzy matching
        for word in idea.split():
            if len(word) > 2:
                for keyword in template["keywords"]:
                    if word in keyword or keyword in word:
                        score += 10
                if word in template["description"].lower():
                    score += 5

        # Filter by difficulty
        if difficulty != "any" and template["difficulty"].lower() != difficulty.lower():
            score -= 20

        # Filter by brick count
        if template["bricks"] > max_bricks:
            score -= 30

        if score > 0:
            suggestions.append({
                "id": key, "score": score, **template
            })

    suggestions.sort(key=lambda x: x["score"], reverse=True)

    # If no matches, suggest random popular ones
    if not suggestions:
        popular = random.sample(list(AI_DESIGN_TEMPLATES.keys()), min(5, len(AI_DESIGN_TEMPLATES)))
        for key in popular:
            suggestions.append({
                "id": key, "score": 0, **AI_DESIGN_TEMPLATES[key]
            })

    return {
        "suggestions": suggestions[:8],
        "query": idea,
        "tip": "Try describing what you want: 'a house with a garden' or 'a spaceship with wings'",
    }


@router.get("/ai/random")
async def ai_random_challenge():
    """Get a random design challenge"""
    challenges = [
        {"theme": "🏗️ Architecture", "challenge": "Build the tallest tower using only 2x2 bricks", "difficulty": "Medium"},
        {"theme": "🎨 Art", "challenge": "Create a mosaic portrait using 1x1 flat pieces", "difficulty": "Hard"},
        {"theme": "🚗 Vehicles", "challenge": "Design a car that could actually roll", "difficulty": "Medium"},
        {"theme": "🌿 Nature", "challenge": "Build a garden scene with at least 3 different plants", "difficulty": "Easy"},
        {"theme": "🏰 Fantasy", "challenge": "Create a dragon's lair with treasure", "difficulty": "Hard"},
        {"theme": "🚀 Space", "challenge": "Design a Mars colony base", "difficulty": "Expert"},
        {"theme": "🎮 Gaming", "challenge": "Recreate a character from your favorite game", "difficulty": "Medium"},
        {"theme": "🍕 Food", "challenge": "Build a life-size food item", "difficulty": "Easy"},
        {"theme": "🎵 Music", "challenge": "Create a musical instrument display", "difficulty": "Medium"},
        {"theme": "🐾 Animals", "challenge": "Build a zoo with at least 5 different animals", "difficulty": "Hard"},
        {"theme": "🏯 Japan", "challenge": "Build a Japanese zen garden with pagoda", "difficulty": "Medium"},
        {"theme": "⚡ Mecha", "challenge": "Design a transforming robot", "difficulty": "Expert"},
    ]
    return {"challenge": random.choice(challenges)}


# ========== 3. MULTI-FLOOR BUILDING SYSTEM ==========

@router.post("/building/floors")
async def generate_floors(request: Request):
    """Generate multi-floor building structure"""
    data = await request.json()
    floors = data.get("floors", 3)
    width = data.get("width", 8)  # in studs
    depth = data.get("depth", 8)  # in studs
    style = data.get("style", "modern")  # modern, classic, japanese, industrial
    include_interior = data.get("include_interior", True)

    building_bricks = []
    floor_height = 4  # bricks per floor

    # Color schemes by style
    styles = {
        "modern": {"wall": "white", "accent": "dark_blue", "floor_color": "light_gray", "roof": "dark_gray"},
        "classic": {"wall": "red", "accent": "white", "floor_color": "tan", "roof": "dark_gray"},
        "japanese": {"wall": "white", "accent": "brown", "floor_color": "tan", "roof": "dark_red"},
        "industrial": {"wall": "dark_gray", "accent": "orange", "floor_color": "dark_gray", "roof": "light_gray"},
    }
    colors = styles.get(style, styles["modern"])

    for floor_num in range(floors):
        z_base = floor_num * floor_height

        # Floor plate
        for x in range(0, width, 4):
            for y in range(0, depth, 4):
                building_bricks.append({
                    "type": "2x4_flat", "x": x, "y": y, "z": z_base,
                    "color": colors["floor_color"], "floor": floor_num,
                    "label": f"Floor {floor_num + 1} base"
                })

        # Walls
        for h in range(1, floor_height):
            z = z_base + h
            # Front wall
            for x in range(0, width, 4):
                building_bricks.append({
                    "type": "2x4", "x": x, "y": 0, "z": z,
                    "color": colors["wall"], "floor": floor_num,
                })
            # Back wall
            for x in range(0, width, 4):
                building_bricks.append({
                    "type": "2x4", "x": x, "y": depth - 2, "z": z,
                    "color": colors["wall"], "floor": floor_num,
                })
            # Left wall
            for y in range(2, depth - 2, 4):
                building_bricks.append({
                    "type": "2x4", "x": 0, "y": y, "z": z,
                    "color": colors["wall"], "floor": floor_num,
                    "rotation": 90,
                })
            # Right wall
            for y in range(2, depth - 2, 4):
                building_bricks.append({
                    "type": "2x4", "x": width - 2, "y": y, "z": z,
                    "color": colors["wall"], "floor": floor_num,
                    "rotation": 90,
                })

        # Interior furniture (if requested)
        if include_interior:
            cx = width // 2
            cy = depth // 2
            if floor_num == 0:  # Ground floor — living room
                building_bricks.append({"type": "2x4", "x": cx-2, "y": cy, "z": z_base+1, "color": "brown", "label": "Table"})
                building_bricks.append({"type": "2x2", "x": cx-2, "y": cy-2, "z": z_base+1, "color": "blue", "label": "Chair"})
            elif floor_num == 1:  # Second floor — bedroom
                building_bricks.append({"type": "2x4", "x": cx-2, "y": cy, "z": z_base+1, "color": "white", "label": "Bed"})
                building_bricks.append({"type": "1x2", "x": cx+2, "y": cy, "z": z_base+1, "color": "brown", "label": "Nightstand"})

        # Windows (accent color gaps in walls)
        if floor_num > 0:
            # Front windows
            building_bricks.append({
                "type": "1x2", "x": width//3, "y": 0, "z": z_base+2,
                "color": "cyan", "label": "Window"
            })
            building_bricks.append({
                "type": "1x2", "x": width*2//3, "y": 0, "z": z_base+2,
                "color": "cyan", "label": "Window"
            })

    # Roof
    z_roof = floors * floor_height
    if style == "japanese":
        # Curved Japanese roof
        for x in range(0, width, 4):
            building_bricks.append({"type": "2x4_slope", "x": x, "y": 0, "z": z_roof, "color": colors["roof"]})
            building_bricks.append({"type": "2x4_slope", "x": x, "y": depth-2, "z": z_roof, "color": colors["roof"], "rotation": 180})
    else:
        # Flat roof
        for x in range(0, width, 4):
            for y in range(0, depth, 4):
                building_bricks.append({"type": "2x4_flat", "x": x, "y": y, "z": z_roof, "color": colors["roof"]})

    return {
        "building": {
            "floors": floors,
            "width": width,
            "depth": depth,
            "style": style,
            "bricks": building_bricks,
            "brick_count": len(building_bricks),
            "height_mm": floors * floor_height * 9.6,
        }
    }


# ========== 4. PHYSICS / STRUCTURAL INTEGRITY CHECKER ==========

@router.post("/physics/check")
async def check_structural_integrity(request: Request):
    """Check if a design is structurally sound — can it stand? Is it printable?"""
    data = await request.json()
    bricks = data.get("bricks", [])

    issues = []
    warnings = []
    score = 100  # Start at 100, deduct for issues

    if not bricks:
        return JSONResponse({"error": "No bricks to check"}, status_code=400)

    # 1. Check for floating bricks (no support below)
    brick_positions = set()
    for b in bricks:
        brick_positions.add((b.get("x", 0), b.get("y", 0), b.get("z", 0)))

    floating_count = 0
    for b in bricks:
        z = b.get("z", 0)
        if z > 0:
            x, y = b.get("x", 0), b.get("y", 0)
            # Check if there's any brick below (within range)
            has_support = False
            for dx in range(-1, 3):
                for dy in range(-1, 3):
                    if (x + dx, y + dy, z - 1) in brick_positions:
                        has_support = True
                        break
                if has_support:
                    break
            if not has_support:
                floating_count += 1
                score -= 5

    if floating_count > 0:
        issues.append({
            "type": "floating",
            "severity": "high",
            "message": f"{floating_count} brick(s) have no support below them — they will fall!",
            "fix": "Add bricks underneath floating pieces or connect them to nearby bricks",
        })

    # 2. Check center of gravity
    if bricks:
        avg_x = sum(b.get("x", 0) for b in bricks) / len(bricks)
        avg_y = sum(b.get("y", 0) for b in bricks) / len(bricks)
        max_z = max(b.get("z", 0) for b in bricks)

        # Check base footprint
        base_bricks = [b for b in bricks if b.get("z", 0) == 0]
        if base_bricks:
            base_min_x = min(b.get("x", 0) for b in base_bricks)
            base_max_x = max(b.get("x", 0) for b in base_bricks) + 2
            base_min_y = min(b.get("y", 0) for b in base_bricks)
            base_max_y = max(b.get("y", 0) for b in base_bricks) + 2

            if avg_x < base_min_x or avg_x > base_max_x:
                issues.append({
                    "type": "balance",
                    "severity": "medium",
                    "message": "Center of gravity is outside the base — design may tip over!",
                    "fix": "Widen the base or center the upper portions",
                })
                score -= 15
        else:
            issues.append({
                "type": "no_base",
                "severity": "high",
                "message": "No bricks at ground level (z=0) — design has no base!",
                "fix": "Add a foundation layer at z=0",
            })
            score -= 25

    # 3. Check for 3D printability
    if max_z > 30:
        warnings.append({
            "type": "tall",
            "severity": "low",
            "message": f"Design is very tall ({max_z} layers) — may need supports for 3D printing",
            "fix": "Consider splitting into sections for easier printing",
        })
        score -= 5

    # 4. Check for overhangs (problematic for 3D printing)
    overhang_count = 0
    for b in bricks:
        x, y, z = b.get("x", 0), b.get("y", 0), b.get("z", 0)
        if z > 0:
            # Check if brick extends past the one below
            has_direct_support = (x, y, z-1) in brick_positions
            if not has_direct_support:
                overhang_count += 1

    if overhang_count > len(bricks) * 0.3:
        warnings.append({
            "type": "overhangs",
            "severity": "medium",
            "message": f"{overhang_count} bricks have overhangs — may need supports for 3D printing",
            "fix": "Redesign with less overhang or plan for support material",
        })
        score -= 10

    # 5. Check connectivity
    if len(bricks) > 1:
        # Simple check: are all bricks connected?
        connected = set()
        connected.add(0)
        changed = True
        while changed:
            changed = False
            for i, b in enumerate(bricks):
                if i in connected:
                    continue
                x1, y1, z1 = b.get("x", 0), b.get("y", 0), b.get("z", 0)
                for j in connected.copy():
                    x2, y2, z2 = bricks[j].get("x", 0), bricks[j].get("y", 0), bricks[j].get("z", 0)
                    dist = abs(x1-x2) + abs(y1-y2) + abs(z1-z2)
                    if dist <= 4:  # Adjacent
                        connected.add(i)
                        changed = True
                        break

        disconnected = len(bricks) - len(connected)
        if disconnected > 0:
            warnings.append({
                "type": "disconnected",
                "severity": "medium",
                "message": f"{disconnected} brick(s) appear disconnected from the main structure",
                "fix": "Connect all pieces or they'll be separate prints",
            })
            score -= 10

    score = max(0, min(100, score))

    return {
        "structural_analysis": {
            "score": score,
            "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F",
            "issues": issues,
            "warnings": warnings,
            "stats": {
                "total_bricks": len(bricks),
                "floating_bricks": floating_count,
                "max_height": max_z if bricks else 0,
                "overhang_count": overhang_count,
            },
            "printability": "Easy" if score >= 80 else "Moderate" if score >= 60 else "Difficult",
        }
    }


# ========== 5. TEXTURE & DECAL SYSTEM ==========

DECALS = {
    "faces": [
        {"id": "smile", "name": "Smiley Face", "emoji": "😊", "category": "faces"},
        {"id": "wink", "name": "Winking Face", "emoji": "😉", "category": "faces"},
        {"id": "cool", "name": "Cool Face", "emoji": "😎", "category": "faces"},
        {"id": "angry", "name": "Angry Face", "emoji": "😠", "category": "faces"},
        {"id": "robot", "name": "Robot Face", "emoji": "🤖", "category": "faces"},
    ],
    "patterns": [
        {"id": "stripes", "name": "Horizontal Stripes", "emoji": "🏳️", "category": "patterns"},
        {"id": "dots", "name": "Polka Dots", "emoji": "⚫", "category": "patterns"},
        {"id": "checker", "name": "Checkerboard", "emoji": "🏁", "category": "patterns"},
        {"id": "zigzag", "name": "Zigzag", "emoji": "⚡", "category": "patterns"},
        {"id": "gradient", "name": "Gradient", "emoji": "🌈", "category": "patterns"},
    ],
    "text": [
        {"id": "numbers", "name": "Numbers (0-9)", "category": "text"},
        {"id": "letters", "name": "Letters (A-Z)", "category": "text"},
        {"id": "kanji", "name": "Japanese Kanji", "category": "text"},
    ],
    "themed": [
        {"id": "fire", "name": "Fire Pattern", "emoji": "🔥", "category": "themed"},
        {"id": "water", "name": "Water Pattern", "emoji": "🌊", "category": "themed"},
        {"id": "stars", "name": "Star Pattern", "emoji": "⭐", "category": "themed"},
        {"id": "heart", "name": "Heart Pattern", "emoji": "❤️", "category": "themed"},
        {"id": "leaf", "name": "Leaf Pattern", "emoji": "🍃", "category": "themed"},
        {"id": "sakura", "name": "Cherry Blossom", "emoji": "🌸", "category": "themed"},
    ],
}

TEXTURES = {
    "smooth": {"name": "Smooth (default)", "roughness": 0.2, "icon": "✨"},
    "matte": {"name": "Matte Finish", "roughness": 0.6, "icon": "🎨"},
    "glossy": {"name": "High Gloss", "roughness": 0.05, "icon": "💎"},
    "metallic": {"name": "Metallic", "roughness": 0.3, "metallic": 0.8, "icon": "🪙"},
    "chrome": {"name": "Chrome", "roughness": 0.05, "metallic": 1.0, "icon": "🪞"},
    "wood": {"name": "Wood Grain", "roughness": 0.5, "icon": "🪵"},
    "marble": {"name": "Marble", "roughness": 0.15, "icon": "🏛️"},
    "rubber": {"name": "Rubber/Matte", "roughness": 0.9, "icon": "🏐"},
    "transparent": {"name": "Transparent", "roughness": 0.1, "opacity": 0.3, "icon": "🔮"},
    "glow": {"name": "Glow in Dark", "roughness": 0.3, "emissive": True, "icon": "💡"},
}

@router.get("/decals")
async def get_decals():
    """Get all available decals and textures"""
    return {"decals": DECALS, "textures": TEXTURES}


@router.post("/decals/apply")
async def apply_decal(request: Request):
    """Apply a decal to a specific brick"""
    data = await request.json()
    brick_index = data.get("brick_index", 0)
    decal_id = data.get("decal_id", "smile")
    face = data.get("face", "front")  # front, back, left, right, top
    texture = data.get("texture", "smooth")

    return {
        "applied": {
            "brick_index": brick_index,
            "decal_id": decal_id,
            "face": face,
            "texture": texture,
        }
    }


# ========== 6. COMMUNITY DESIGNS INTEGRATION ==========

# Simulated community designs (in production, would fetch from APIs)
COMMUNITY_DESIGNS = [
    {"id": "community_1", "name": "Modular City Street", "author": "BrickMaster2024", "likes": 3420, "downloads": 12500, "source": "Printables", "url": "https://www.printables.com/model/lego-city", "category": "buildings", "difficulty": "Expert"},
    {"id": "community_2", "name": "Articulated Dragon", "author": "DragonBuilder", "likes": 5600, "downloads": 28000, "source": "Thingiverse", "url": "https://www.thingiverse.com/thing/dragon", "category": "creatures", "difficulty": "Hard"},
    {"id": "community_3", "name": "Working Clock Tower", "author": "TechnicGenius", "likes": 2100, "downloads": 8900, "source": "MyMiniFactory", "url": "https://www.myminifactory.com/object/clock", "category": "technic", "difficulty": "Expert"},
    {"id": "community_4", "name": "Cherry Blossom Tree", "author": "SakuraBuilder", "likes": 4200, "downloads": 15600, "source": "Printables", "url": "https://www.printables.com/model/sakura-tree", "category": "nature", "difficulty": "Medium"},
    {"id": "community_5", "name": "Mini Gundam RX-78", "author": "MechaFan", "likes": 8900, "downloads": 42000, "source": "Thingiverse", "url": "https://www.thingiverse.com/thing/gundam", "category": "mecha", "difficulty": "Hard"},
    {"id": "community_6", "name": "Functional Fidget Cube", "author": "PrintNPlay", "likes": 6700, "downloads": 31000, "source": "Thangs", "url": "https://thangs.com/fidget-cube", "category": "toys", "difficulty": "Easy"},
    {"id": "community_7", "name": "Japanese Castle (Himeji)", "author": "CastleKing", "likes": 3800, "downloads": 14200, "source": "Cults3D", "url": "https://cults3d.com/himeji", "category": "buildings", "difficulty": "Expert"},
    {"id": "community_8", "name": "Customizable Minifig", "author": "FigDesigner", "likes": 9200, "downloads": 55000, "source": "Printables", "url": "https://www.printables.com/model/custom-minifig", "category": "figures", "difficulty": "Easy"},
    {"id": "community_9", "name": "Roller Coaster Track", "author": "ThemeParkFan", "likes": 2900, "downloads": 11000, "source": "Thingiverse", "url": "https://www.thingiverse.com/thing/coaster", "category": "technic", "difficulty": "Expert"},
    {"id": "community_10", "name": "Bonsai Tree", "author": "ZenBuilder", "likes": 7100, "downloads": 33000, "source": "Printables", "url": "https://www.printables.com/model/bonsai", "category": "nature", "difficulty": "Medium"},
]


@router.get("/community/popular")
async def get_popular_designs():
    """Get popular community designs"""
    sorted_designs = sorted(COMMUNITY_DESIGNS, key=lambda x: x["likes"], reverse=True)
    return {"designs": sorted_designs}


@router.get("/community/search")
async def search_community(q: str = ""):
    """Search community designs"""
    results = []
    for design in COMMUNITY_DESIGNS:
        if q.lower() in design["name"].lower() or q.lower() in design["category"].lower():
            results.append(design)
    if not results:
        results = random.sample(COMMUNITY_DESIGNS, min(5, len(COMMUNITY_DESIGNS)))
    return {"results": results, "query": q}


# ========== 7. STEP-BY-STEP INSTRUCTION PDF DATA ==========

@router.post("/instructions/pdf-data")
async def generate_instruction_pdf_data(request: Request):
    """Generate data for a printable instruction booklet (like real LEGO)"""
    data = await request.json()
    bricks = data.get("bricks", [])
    design_name = data.get("name", "My Creation")
    author = data.get("author", "Dr. Imokawa")

    # Sort by z-layer
    sorted_bricks = sorted(bricks, key=lambda b: (b.get("z", 0), b.get("x", 0), b.get("y", 0)))

    # Group into steps (by z-layer)
    steps = {}
    for brick in sorted_bricks:
        z = brick.get("z", 0)
        if z not in steps:
            steps[z] = []
        steps[z].append(brick)

    # Build instruction pages
    pages = []

    # Cover page
    pages.append({
        "type": "cover",
        "title": design_name,
        "author": author,
        "brick_count": len(bricks),
        "difficulty": "Easy" if len(bricks) < 30 else "Medium" if len(bricks) < 80 else "Hard",
        "estimated_time": f"{max(5, len(bricks) * 2)} minutes",
    })

    # Parts list page
    parts_count = {}
    for b in bricks:
        key = f"{b.get('type', '2x4')}_{b.get('color', 'red')}"
        parts_count[key] = parts_count.get(key, {
            "type": b.get("type", "2x4"),
            "color": b.get("color", "red"),
            "count": 0
        })
        parts_count[key]["count"] += 1

    pages.append({
        "type": "parts_list",
        "parts": list(parts_count.values()),
        "total_parts": len(bricks),
    })

    # Step pages
    for step_num, (z, layer_bricks) in enumerate(sorted(steps.items()), 1):
        cumulative = sum(len(steps[k]) for k in sorted(steps.keys()) if k <= z)
        pages.append({
            "type": "step",
            "step_number": step_num,
            "layer": z,
            "new_bricks": layer_bricks,
            "new_brick_count": len(layer_bricks),
            "cumulative_count": cumulative,
            "progress_percent": round(cumulative / max(len(bricks), 1) * 100),
            "instruction": f"Place {len(layer_bricks)} brick(s) at layer {z + 1}",
        })

    # Completion page
    pages.append({
        "type": "completion",
        "message": f"🎉 Congratulations! You've completed {design_name}!",
        "total_bricks": len(bricks),
        "total_steps": len(steps),
    })

    return {
        "instruction_booklet": {
            "pages": pages,
            "page_count": len(pages),
            "design_name": design_name,
            "format": "A5 landscape (like real LEGO instructions)",
        }
    }
