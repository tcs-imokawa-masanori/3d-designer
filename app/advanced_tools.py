from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json, math, time, uuid, random, copy

router = APIRouter(prefix="/api/tools", tags=["tools"])

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

COLOR_PALETTES = {
    "Classic": ["#CC0000", "#0055BF", "#FFD500", "#00852B", "#FFFFFF", "#1B2A34"],
    "Pastel": ["#FC97AC", "#E4CD9E", "#BBE90B", "#00BCD4", "#FFFFFF", "#9BA19D"],
    "Earth Tones": ["#583927", "#E4CD9E", "#00451A", "#6C6E68", "#720E0F", "#5A7184"],
    "Ocean": ["#0055BF", "#0A3463", "#00BCD4", "#5A7184", "#FFFFFF", "#9BA19D"],
    "Sunset": ["#CC0000", "#FF7E14", "#FFD500", "#E91E63", "#720E0F", "#FC97AC"],
    "Monochrome": ["#FFFFFF", "#9BA19D", "#6C6E68", "#1B2A34", "#5A7184", "#E4CD9E"],
    "Neon": ["#BBE90B", "#00BCD4", "#E91E63", "#FF7E14", "#FFD500", "#FC97AC"],
    "Forest": ["#00852B", "#00451A", "#583927", "#BBE90B", "#E4CD9E", "#6C6E68"],
}


def _compute_centroid(bricks):
    """Compute the centroid of a list of bricks based on their x, y positions."""
    if not bricks:
        return 0.0, 0.0
    cx = sum(b.get("x", 0) for b in bricks) / len(bricks)
    cy = sum(b.get("y", 0) for b in bricks) / len(bricks)
    return cx, cy


# ---------------------------------------------------------------------------
# 1. POST /rotate-design
# ---------------------------------------------------------------------------
@router.post("/rotate-design")
async def rotate_design(request: Request):
    """Rotate an entire design by 90, 180, or 270 degrees around the centroid."""
    body = await request.json()
    bricks = body.get("bricks", [])
    angle = body.get("angle", 90)

    if angle not in (90, 180, 270):
        return JSONResponse(
            status_code=400,
            content={"error": "Angle must be 90, 180, or 270 degrees."},
        )

    if not bricks:
        return JSONResponse(content={"bricks": [], "angle": angle})

    cx, cy = _compute_centroid(bricks)
    rad = math.radians(angle)
    cos_a = round(math.cos(rad))
    sin_a = round(math.sin(rad))

    rotated = []
    for brick in bricks:
        b = copy.deepcopy(brick)
        dx = b.get("x", 0) - cx
        dy = b.get("y", 0) - cy
        b["x"] = round(cx + dx * cos_a - dy * sin_a, 4)
        b["y"] = round(cy + dx * sin_a + dy * cos_a, 4)
        rotated.append(b)

    return JSONResponse(content={
        "bricks": rotated,
        "angle": angle,
        "count": len(rotated),
    })


# ---------------------------------------------------------------------------
# 2. POST /scale
# ---------------------------------------------------------------------------
@router.post("/scale")
async def scale_design(request: Request):
    """Scale a design up or down by the given factor."""
    body = await request.json()
    bricks = body.get("bricks", [])
    factor = body.get("scale_factor", 1)

    if factor not in (0.5, 1, 2, 3):
        return JSONResponse(
            status_code=400,
            content={"error": "Scale factor must be one of: 0.5, 1, 2, 3."},
        )

    if not bricks:
        return JSONResponse(content={"bricks": [], "scale_factor": factor})

    cx, cy = _compute_centroid(bricks)
    cz = sum(b.get("z", 0) for b in bricks) / len(bricks)

    scaled = []
    for brick in bricks:
        b = copy.deepcopy(brick)
        b["x"] = round(cx + (b.get("x", 0) - cx) * factor, 4)
        b["y"] = round(cy + (b.get("y", 0) - cy) * factor, 4)
        b["z"] = round(cz + (b.get("z", 0) - cz) * factor, 4)
        # Scale brick dimensions if present
        if "width" in b:
            b["width"] = round(b["width"] * factor, 4)
        if "height" in b:
            b["height"] = round(b["height"] * factor, 4)
        if "depth" in b:
            b["depth"] = round(b["depth"] * factor, 4)
        scaled.append(b)

    return JSONResponse(content={
        "bricks": scaled,
        "scale_factor": factor,
        "count": len(scaled),
    })


# ---------------------------------------------------------------------------
# 3. POST /explode-view
# ---------------------------------------------------------------------------
@router.post("/explode-view")
async def explode_view(request: Request):
    """Generate an exploded view by separating layers along the Z axis."""
    body = await request.json()
    bricks = body.get("bricks", [])
    gap_factor = body.get("gap_factor", 2.0)

    if not bricks:
        return JSONResponse(content={"bricks": [], "gap_factor": gap_factor})

    # Determine unique Z layers and sort them
    z_values = sorted(set(b.get("z", 0) for b in bricks))
    layer_index = {z: i for i, z in enumerate(z_values)}

    exploded = []
    for brick in bricks:
        b = copy.deepcopy(brick)
        original_z = b.get("z", 0)
        idx = layer_index[original_z]
        b["z"] = round(original_z + idx * gap_factor, 4)
        b["_original_z"] = original_z
        exploded.append(b)

    return JSONResponse(content={
        "bricks": exploded,
        "gap_factor": gap_factor,
        "layers": len(z_values),
        "count": len(exploded),
    })


# ---------------------------------------------------------------------------
# 4. POST /color-replace
# ---------------------------------------------------------------------------
@router.post("/color-replace")
async def color_replace(request: Request):
    """Replace one color with another across the entire design."""
    body = await request.json()
    bricks = body.get("bricks", [])
    old_color = body.get("old_color", "").strip()
    new_color = body.get("new_color", "").strip()

    if not old_color or not new_color:
        return JSONResponse(
            status_code=400,
            content={"error": "Both old_color and new_color are required."},
        )

    replaced_count = 0
    updated = []
    for brick in bricks:
        b = copy.deepcopy(brick)
        brick_color = b.get("color", "")
        if brick_color.lower() == old_color.lower():
            b["color"] = new_color
            replaced_count += 1
        updated.append(b)

    return JSONResponse(content={
        "bricks": updated,
        "old_color": old_color,
        "new_color": new_color,
        "replaced_count": replaced_count,
        "total_count": len(updated),
    })


# ---------------------------------------------------------------------------
# 5. POST /randomize-colors
# ---------------------------------------------------------------------------
@router.post("/randomize-colors")
async def randomize_colors(request: Request):
    """Randomize all brick colors using the LEGO color palette."""
    body = await request.json()
    bricks = body.get("bricks", [])

    color_values = list(LEGO_COLORS.values())

    randomized = []
    for brick in bricks:
        b = copy.deepcopy(brick)
        b["color"] = random.choice(color_values)
        randomized.append(b)

    return JSONResponse(content={
        "bricks": randomized,
        "palette_used": "LEGO Standard",
        "count": len(randomized),
    })


# ---------------------------------------------------------------------------
# 6. POST /snap-check
# ---------------------------------------------------------------------------
@router.post("/snap-check")
async def snap_check(request: Request):
    """Check for overlapping and floating bricks in the design."""
    body = await request.json()
    bricks = body.get("bricks", [])

    issues = []
    positions = {}

    # Build a set of occupied positions for quick lookup
    occupied = set()
    for i, brick in enumerate(bricks):
        x = brick.get("x", 0)
        y = brick.get("y", 0)
        z = brick.get("z", 0)
        pos_key = (x, y, z)

        # Check for overlapping bricks (same position)
        if pos_key in positions:
            issues.append({
                "type": "overlap",
                "severity": "error",
                "message": f"Brick {i} overlaps with brick {positions[pos_key]} at position ({x}, {y}, {z}).",
                "brick_indices": [positions[pos_key], i],
                "position": {"x": x, "y": y, "z": z},
            })
        else:
            positions[pos_key] = i

        occupied.add(pos_key)

    # Check for floating bricks (not on ground level and no brick directly below)
    for i, brick in enumerate(bricks):
        x = brick.get("x", 0)
        y = brick.get("y", 0)
        z = brick.get("z", 0)

        if z > 0:
            below = (x, y, z - 1)
            if below not in occupied:
                issues.append({
                    "type": "floating",
                    "severity": "warning",
                    "message": f"Brick {i} at ({x}, {y}, {z}) has no support below.",
                    "brick_index": i,
                    "position": {"x": x, "y": y, "z": z},
                })

    error_count = sum(1 for iss in issues if iss["severity"] == "error")
    warning_count = sum(1 for iss in issues if iss["severity"] == "warning")

    return JSONResponse(content={
        "issues": issues,
        "total_issues": len(issues),
        "errors": error_count,
        "warnings": warning_count,
        "brick_count": len(bricks),
        "valid": len(issues) == 0,
    })


# ---------------------------------------------------------------------------
# 7. POST /hollow
# ---------------------------------------------------------------------------
@router.post("/hollow")
async def hollow_design(request: Request):
    """Remove interior bricks, keeping only the exterior shell."""
    body = await request.json()
    bricks = body.get("bricks", [])

    if not bricks:
        return JSONResponse(content={"bricks": [], "removed": 0})

    # Build a set of all occupied positions
    occupied = set()
    for brick in bricks:
        pos = (brick.get("x", 0), brick.get("y", 0), brick.get("z", 0))
        occupied.add(pos)

    # A brick is interior if all 6 neighbors are occupied
    exterior = []
    removed_count = 0
    neighbors = [
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    ]

    for brick in bricks:
        x = brick.get("x", 0)
        y = brick.get("y", 0)
        z = brick.get("z", 0)

        is_interior = True
        for dx, dy, dz in neighbors:
            if (x + dx, y + dy, z + dz) not in occupied:
                is_interior = False
                break

        if is_interior:
            removed_count += 1
        else:
            exterior.append(copy.deepcopy(brick))

    return JSONResponse(content={
        "bricks": exterior,
        "original_count": len(bricks),
        "removed": removed_count,
        "remaining": len(exterior),
    })


# ---------------------------------------------------------------------------
# 8. POST /fill
# ---------------------------------------------------------------------------
@router.post("/fill")
async def fill_volume(request: Request):
    """Fill a bounding box with bricks of the specified type and color."""
    body = await request.json()
    min_x = body.get("min_x", 0)
    min_y = body.get("min_y", 0)
    min_z = body.get("min_z", 0)
    max_x = body.get("max_x", 1)
    max_y = body.get("max_y", 1)
    max_z = body.get("max_z", 1)
    brick_type = body.get("brick_type", "1x1")
    color = body.get("color", "#CC0000")

    # Validate bounds
    if max_x < min_x or max_y < min_y or max_z < min_z:
        return JSONResponse(
            status_code=400,
            content={"error": "max coordinates must be >= min coordinates."},
        )

    # Safety limit
    volume = (max_x - min_x + 1) * (max_y - min_y + 1) * (max_z - min_z + 1)
    if volume > 10000:
        return JSONResponse(
            status_code=400,
            content={"error": f"Fill volume ({volume}) exceeds safety limit of 10000 bricks."},
        )

    filled = []
    for x in range(int(min_x), int(max_x) + 1):
        for y in range(int(min_y), int(max_y) + 1):
            for z in range(int(min_z), int(max_z) + 1):
                filled.append({
                    "id": str(uuid.uuid4()),
                    "x": x,
                    "y": y,
                    "z": z,
                    "type": brick_type,
                    "color": color,
                })

    return JSONResponse(content={
        "bricks": filled,
        "count": len(filled),
        "bounds": {
            "min": {"x": min_x, "y": min_y, "z": min_z},
            "max": {"x": max_x, "y": max_y, "z": max_z},
        },
        "brick_type": brick_type,
        "color": color,
    })


# ---------------------------------------------------------------------------
# 9. POST /array
# ---------------------------------------------------------------------------
@router.post("/array")
async def array_bricks(request: Request):
    """Create an array/pattern of bricks by duplicating along X, Y, Z axes."""
    body = await request.json()
    brick = body.get("brick", {})
    count_x = body.get("count_x", 1)
    count_y = body.get("count_y", 1)
    count_z = body.get("count_z", 1)
    spacing = body.get("spacing", 1)

    # Safety limit
    total = count_x * count_y * count_z
    if total > 10000:
        return JSONResponse(
            status_code=400,
            content={"error": f"Array size ({total}) exceeds safety limit of 10000 bricks."},
        )

    if total < 1:
        return JSONResponse(
            status_code=400,
            content={"error": "Count values must be at least 1."},
        )

    base_x = brick.get("x", 0)
    base_y = brick.get("y", 0)
    base_z = brick.get("z", 0)

    result = []
    for ix in range(int(count_x)):
        for iy in range(int(count_y)):
            for iz in range(int(count_z)):
                b = copy.deepcopy(brick)
                b["id"] = str(uuid.uuid4())
                b["x"] = round(base_x + ix * spacing, 4)
                b["y"] = round(base_y + iy * spacing, 4)
                b["z"] = round(base_z + iz * spacing, 4)
                result.append(b)

    return JSONResponse(content={
        "bricks": result,
        "count": len(result),
        "pattern": {
            "count_x": count_x,
            "count_y": count_y,
            "count_z": count_z,
            "spacing": spacing,
        },
    })


# ---------------------------------------------------------------------------
# 10. POST /auto-roof
# ---------------------------------------------------------------------------
@router.post("/auto-roof")
async def auto_roof(request: Request):
    """Auto-generate a sloped roof on top of the wall bricks."""
    body = await request.json()
    bricks = body.get("bricks", [])

    if not bricks:
        return JSONResponse(content={"bricks": [], "roof_bricks": [], "message": "No bricks provided."})

    # Determine the top layer (highest Z)
    max_z = max(b.get("z", 0) for b in bricks)
    top_bricks = [b for b in bricks if b.get("z", 0) == max_z]

    if not top_bricks:
        return JSONResponse(content={
            "bricks": bricks,
            "roof_bricks": [],
            "message": "Could not determine top layer.",
        })

    # Get the bounding box of the top layer
    min_x = min(b.get("x", 0) for b in top_bricks)
    max_x_val = max(b.get("x", 0) for b in top_bricks)
    min_y = min(b.get("y", 0) for b in top_bricks)
    max_y_val = max(b.get("y", 0) for b in top_bricks)

    # Generate a simple triangular/sloped roof along the Y axis
    roof_bricks = []
    roof_color = "#CC0000"  # Classic red roof
    width = max_x_val - min_x + 1
    half_width = width / 2.0
    current_z = max_z + 1

    left = min_x
    right = max_x_val

    layer = 0
    while left <= right:
        for x in range(int(left), int(right) + 1):
            for y in range(int(min_y), int(max_y_val) + 1):
                roof_bricks.append({
                    "id": str(uuid.uuid4()),
                    "x": x,
                    "y": y,
                    "z": current_z + layer,
                    "type": "1x1",
                    "color": roof_color,
                    "is_roof": True,
                })
        left += 1
        right -= 1
        layer += 1

    return JSONResponse(content={
        "bricks": bricks + roof_bricks,
        "roof_bricks": roof_bricks,
        "roof_layers": layer,
        "roof_brick_count": len(roof_bricks),
        "total_count": len(bricks) + len(roof_bricks),
    })


# ---------------------------------------------------------------------------
# 11. GET /color-palettes
# ---------------------------------------------------------------------------
@router.get("/color-palettes")
async def get_color_palettes():
    """Return curated LEGO color palettes."""
    palettes = []
    for name, colors in COLOR_PALETTES.items():
        palettes.append({
            "name": name,
            "colors": colors,
            "count": len(colors),
        })

    return JSONResponse(content={
        "palettes": palettes,
        "total": len(palettes),
        "all_lego_colors": LEGO_COLORS,
    })


# ---------------------------------------------------------------------------
# 12. POST /symmetry-check
# ---------------------------------------------------------------------------
@router.post("/symmetry-check")
async def symmetry_check(request: Request):
    """Check if a design is symmetrical along a given axis."""
    body = await request.json()
    bricks = body.get("bricks", [])
    axis = body.get("axis", "x").lower()

    if axis not in ("x", "y", "z"):
        return JSONResponse(
            status_code=400,
            content={"error": "Axis must be 'x', 'y', or 'z'."},
        )

    if not bricks:
        return JSONResponse(content={
            "symmetrical": True,
            "score": 1.0,
            "axis": axis,
            "suggestions": [],
            "message": "No bricks to check.",
        })

    # Find the midpoint along the chosen axis
    axis_values = [b.get(axis, 0) for b in bricks]
    midpoint = (min(axis_values) + max(axis_values)) / 2.0

    # Build a set of positions for quick lookup (using the other two axes + color)
    other_axes = [a for a in ("x", "y", "z") if a != axis]

    # Map each brick to its mirrored position along the axis
    position_set = set()
    for brick in bricks:
        pos = (
            brick.get("x", 0),
            brick.get("y", 0),
            brick.get("z", 0),
            brick.get("color", ""),
        )
        position_set.add(pos)

    matched = 0
    unmatched_bricks = []

    for brick in bricks:
        bx = brick.get("x", 0)
        by = brick.get("y", 0)
        bz = brick.get("z", 0)
        bc = brick.get("color", "")

        # Compute the mirrored coordinate
        mirror = {}
        mirror["x"] = bx
        mirror["y"] = by
        mirror["z"] = bz
        original_val = brick.get(axis, 0)
        mirror[axis] = round(2 * midpoint - original_val, 4)

        mirror_pos = (mirror["x"], mirror["y"], mirror["z"], bc)

        if mirror_pos in position_set:
            matched += 1
        else:
            unmatched_bricks.append({
                "brick_position": {"x": bx, "y": by, "z": bz},
                "expected_mirror": {"x": mirror["x"], "y": mirror["y"], "z": mirror["z"]},
                "color": bc,
            })

    score = matched / len(bricks) if bricks else 1.0

    suggestions = []
    if score < 1.0:
        suggestions.append(
            f"Add {len(unmatched_bricks)} mirrored brick(s) along the {axis.upper()} axis to achieve full symmetry."
        )
    if score >= 0.8 and score < 1.0:
        suggestions.append("Design is nearly symmetrical. Minor adjustments would make it perfect.")
    if score < 0.5:
        suggestions.append("Design has low symmetry. Consider redesigning one half and mirroring it.")

    return JSONResponse(content={
        "symmetrical": score == 1.0,
        "score": round(score, 4),
        "axis": axis,
        "midpoint": midpoint,
        "matched_bricks": matched,
        "unmatched_bricks": unmatched_bricks[:50],  # Limit output size
        "total_bricks": len(bricks),
        "suggestions": suggestions,
    })
