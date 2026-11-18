"""Measure facial eye geometry and eyebrow targets without modifying the blend."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import sha256


EYE_OBJECTS = {
    "L": ("NMM_Eyeball.L", "NMM_Iris.L", "NMM_Pupil.L"),
    "R": ("NMM_Eyeball.R", "NMM_Iris.R", "NMM_Pupil.R"),
}
BROW_TARGETS = ("NMM_BROW_RAISE_L", "NMM_BROW_RAISE_R")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def eye_basis(armature, side):
    bone = armature.data.bones["eye.%s" % side]
    forward = (bone.tail_local - bone.head_local).normalized()
    lateral = Vector((1.0, 0.0, 0.0))
    lateral = (lateral - forward * forward.dot(lateral)).normalized()
    up = forward.cross(lateral).normalized()
    return lateral, forward, up


def projected_bounds(obj, basis):
    lateral, forward, up = basis
    source = obj.data.shape_keys.reference_key.data if obj.data.shape_keys else obj.data.vertices
    points = [vertex.co for vertex in source]
    center = sum(points, Vector()) / len(points)
    rows = {
        "lateral": [lateral.dot(point - center) for point in points],
        "forward": [forward.dot(point - center) for point in points],
        "up": [up.dot(point - center) for point in points],
    }
    return {
        "center_local_m": [round(value, 9) for value in center],
        "dimensions_m": {
            axis: round(max(values) - min(values), 9)
            for axis, values in rows.items()
        },
        "extents_m": {
            axis: [round(min(values), 9), round(max(values), 9)]
            for axis, values in rows.items()
        },
        "vertices": len(points),
    }


def socket_proxy(body, eye_center, basis):
    """Measure the nearby facial-surface envelope around the eye aperture.

    The base mesh has no explicit socket object. This deterministic proxy uses
    an annulus around the eye bone centre and reports its local width, height
    and forward surface distribution rather than inventing anatomical points.
    """
    lateral, forward, up = basis
    selected = []
    for vertex in body.data.shape_keys.reference_key.data:
        relative = vertex.co - eye_center
        x = lateral.dot(relative)
        z = up.dot(relative)
        forward_distance = forward.dot(relative)
        radial = math.sqrt((x / 0.034) ** 2 + (z / 0.022) ** 2)
        if 0.62 <= radial <= 1.18 and abs(x) <= 0.040 and abs(z) <= 0.028 and -0.025 <= forward_distance <= 0.060:
            selected.append((x, forward_distance, z))
    if not selected:
        raise RuntimeError("Unable to measure eye socket proxy")
    forward_values = sorted(row[1] for row in selected)
    return {
        "method": "body Basis vertices in deterministic elliptical annulus around eye bone centre",
        "sample_count": len(selected),
        "width_m": round(max(row[0] for row in selected) - min(row[0] for row in selected), 9),
        "height_m": round(max(row[2] for row in selected) - min(row[2] for row in selected), 9),
        "forward_surface_m": {
            "min": round(forward_values[0], 9),
            "median": round(forward_values[len(forward_values) // 2], 9),
            "max": round(forward_values[-1], 9),
        },
    }


def brow_record(body, name):
    keys = body.data.shape_keys.key_blocks
    basis = body.data.shape_keys.reference_key
    key = keys[name]
    deltas = [(target.co - source.co) for target, source in zip(key.data, basis.data)]
    lengths = [delta.length for delta in deltas]
    moved = [value for value in lengths if value > 1e-7]
    vertical = [delta.z for delta in deltas if delta.length > 1e-7]
    forward = [delta.y for delta in deltas if delta.length > 1e-7]
    return {
        "name": name,
        "moved_vertices": len(moved),
        "max_delta_m": round(max(moved), 9),
        "mean_delta_m": round(sum(moved) / len(moved), 9),
        "max_up_m": round(max(vertical), 9),
        "mean_up_m": round(sum(vertical) / len(vertical), 9),
        "forward_delta_range_m": [round(min(forward), 9), round(max(forward), 9)],
        "interpolation": {
            "0.0_max_delta_m": 0.0,
            "0.5_max_delta_m": round(max(moved) * 0.5, 9),
            "1.0_max_delta_m": round(max(moved), 9),
        },
    }


def main():
    args = arguments()
    body = bpy.data.objects.get("Human")
    armature = bpy.data.objects.get("Human.rig")
    if not body or not armature or not body.data.shape_keys:
        raise RuntimeError("Human/Human.rig/Shape Keys missing")
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))

    eyes = {}
    for side, names in EYE_OBJECTS.items():
        objects = [bpy.data.objects.get(name) for name in names]
        if any(obj is None for obj in objects):
            raise RuntimeError("Missing eye objects for %s" % side)
        basis = eye_basis(armature, side)
        eyeball = projected_bounds(objects[0], basis)
        iris = projected_bounds(objects[1], basis)
        pupil = projected_bounds(objects[2], basis)
        eye_center = Vector(eyeball["center_local_m"])
        socket = socket_proxy(body, eye_center, basis)
        eyeball_front = eyeball["extents_m"]["forward"][1]
        eyes[side] = {
            "bone": "eye.%s" % side,
            "bone_head_local_m": [round(v, 9) for v in armature.data.bones["eye.%s" % side].head_local],
            "bone_tail_local_m": [round(v, 9) for v in armature.data.bones["eye.%s" % side].tail_local],
            "eyeball": eyeball,
            "iris": iris,
            "pupil": pupil,
            "socket_proxy": socket,
            "protrusion_vs_socket_median_m": round(eyeball_front - socket["forward_surface_m"]["median"], 9),
        }

    left = Vector(eyes["L"]["eyeball"]["center_local_m"])
    right = Vector(eyes["R"]["eyeball"]["center_local_m"])
    symmetry = {
        "center_x_sum_abs_m": round(abs(left.x + right.x), 9),
        "center_y_difference_abs_m": round(abs(left.y - right.y), 9),
        "center_z_difference_abs_m": round(abs(left.z - right.z), 9),
        "diameter_difference_abs_m": round(abs(
            eyes["L"]["eyeball"]["dimensions_m"]["lateral"]
            - eyes["R"]["eyeball"]["dimensions_m"]["lateral"]
        ), 9),
    }
    report = {
        "schema_version": 1,
        "artifact": "facial_geometry_inspection",
        "status": "PASS",
        "source": {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)},
        "blender_version": bpy.app.version_string,
        "bone_count": len(armature.data.bones),
        "eyes": eyes,
        "eye_symmetry": symmetry,
        "brows": [brow_record(body, name) for name in BROW_TARGETS],
    }
    output = Path(args.report).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS facial geometry inspection: %s" % output)


if __name__ == "__main__":
    main()
