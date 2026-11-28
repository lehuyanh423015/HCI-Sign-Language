"""Measure two-hand contact, hand orientation and smoothness of a sign Action.

    blender -b blender/working/signs/S004/S004.blend --python blender/scripts/measure_hand_contact.py -- \
        --output blender/working/signs/S004/evidence/contact-metrics.json --window 22 53

For each frame the script evaluates the pose and reports:
- ``gap_cm``: height of the lowest right-hand finger joint above the left palm centre, along the left palm
  normal. Joints sit inside the mesh, so about 2–3 cm means the skin surfaces touch; negative means the
  right hand passes through the left palm.
- ``lateral_cm``: distance of the right fist centre from the left palm centre, across the palm.
- ``left_palm_up``: Z component of the left palm normal (1 = palm facing straight up).
- ``thumb_up``: Z component of the right thumb direction (1 = pointing straight up).
It also reports per-bone angular speed and its frame-to-frame change, to find pops and jitter.
Numbers support visual review; they do not replace it.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

BONES = ("upperarm01.R", "lowerarm01.R", "wrist.R", "upperarm01.L", "lowerarm01.L", "wrist.L", "head")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--window", type=int, nargs=2, help="contact window in frames, for the summary")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def main():
    args = arguments()
    arm = bpy.data.objects["Human.rig"]
    scene = bpy.context.scene
    pb = arm.pose.bones
    head = lambda n: pb[n].head.copy()
    rows, quats = {}, {}
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        mcp = [head(f"finger{k}-1.L") for k in (2, 3, 4, 5)]
        centre = (sum(mcp, Vector()) / 4) * 0.65 + head("wrist.L") * 0.35
        fwd = (head("finger3-1.L") - head("wrist.L")).normalized()
        across = (head("finger2-1.L") - head("finger5-1.L")).normalized()
        normal = fwd.cross(across).normalized()
        pts = [head(f"finger{k}-{j}.R") for k in (2, 3, 4, 5) for j in (1, 2, 3)] + [pb[f"finger{k}-3.R"].tail.copy() for k in (2, 3, 4, 5)]
        low = min(pts, key=lambda v: v.dot(normal))
        fist = sum(pts, Vector()) / len(pts)
        lateral = (fist - centre) - normal * (fist - centre).dot(normal)
        thumb = (pb["finger1-3.R"].tail - pb["finger1-2.R"].head).normalized()
        rows[f] = {
            "gap_cm": round((low - centre).dot(normal) * 100, 2),
            "lateral_cm": round(lateral.length * 100, 2),
            "left_palm_up": round(normal.z, 3),
            "thumb_up": round(thumb.z, 3),
        }
        quats[f] = {n: pb[n].rotation_quaternion.copy() for n in BONES}
    frames = sorted(rows)
    motion = {}
    for name in BONES:
        speed = [math.degrees(quats[f][name].rotation_difference(quats[f + 1][name]).angle) for f in frames[:-1]]
        change = [abs(speed[i + 1] - speed[i]) for i in range(len(speed) - 1)]
        motion[name] = {
            "max_deg_per_frame": round(max(speed), 2), "at_frame": frames[speed.index(max(speed))],
            "max_change_deg": round(max(change), 2), "change_at_frame": frames[change.index(max(change)) + 1],
        }
    summary = None
    if args.window:
        a, b = args.window
        w = [rows[f] for f in frames if a <= f <= b]
        pick = lambda k: [r[k] for r in w]
        summary = {
            "frames": [a, b],
            "gap_cm": {"min": min(pick("gap_cm")), "max": max(pick("gap_cm"))},
            "lateral_cm_max": max(pick("lateral_cm")),
            "left_palm_up": {"min": min(pick("left_palm_up")), "max": max(pick("left_palm_up"))},
            "thumb_up": {"min": min(pick("thumb_up")), "max": max(pick("thumb_up"))},
        }
    report = {"schema_version": 1, "artifact": "sign_hand_contact_metrics", "source": Path(bpy.data.filepath).name,
              "summary": summary, "motion": motion, "frames": rows}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS measured {len(rows)} frames -> {args.output}")


if __name__ == "__main__":
    main()
