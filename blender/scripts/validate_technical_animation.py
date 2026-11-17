"""Validate the saved technical animation after reopening its .blend file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import TECHNICAL_BONES, action_fcurves, require_rig, sha256


ACTION_NAME = "TECH_HAND_CONTROL_TEST"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def main():
    args = arguments()
    armature, _mesh = require_rig()
    action = bpy.data.actions.get(ACTION_NAME)
    if action is None:
        raise RuntimeError("Saved action %s was not found" % ACTION_NAME)

    slot = next((item for item in action.slots if item.target_id_type == "OBJECT"), None)
    if slot is None:
        raise RuntimeError("Saved action has no OBJECT slot")

    curves = list(action_fcurves(action, slot))
    animated_bones = sorted(
        {
            curve.data_path.split('pose.bones["', 1)[1].split('"]', 1)[0]
            for curve in curves
            if 'pose.bones["' in curve.data_path
        }
    )
    frames = sorted(
        {
            round(point.co.x, 6)
            for curve in curves
            for point in curve.keyframe_points
        }
    )
    assigned = armature.animation_data is not None and armature.animation_data.action == action
    checks = {
        "action_name_exact": action.name == ACTION_NAME,
        "action_assigned_to_armature": assigned,
        "scene_timing": bpy.context.scene.render.fps == 30 and bpy.context.scene.frame_start == 1 and bpy.context.scene.frame_end == 30,
        "expected_bones_only": animated_bones == sorted(TECHNICAL_BONES),
        "expected_keyframes": len(curves) == 45 and sum(len(curve.keyframe_points) for curve in curves) == 135 and frames == [1.0, 15.0, 30.0],
        "editable_source": Path(bpy.data.filepath).suffix.lower() == ".blend",
    }
    report = {
        "schema_version": 1,
        "artifact": "technical_animation_reload_validation",
        "source_blend": bpy.data.filepath,
        "source_sha256": sha256(bpy.data.filepath),
        "blender_version": bpy.app.version_string,
        "action": {
            "name": action.name,
            "slot_identifier": slot.identifier,
            "fcurve_count": len(curves),
            "keyframe_point_count": sum(len(curve.keyframe_points) for curve in curves),
            "keyframe_frames": frames,
            "animated_bones": animated_bones,
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print("[%s] %s" % ("PASS" if passed else "FAIL", name))
    print("[%s] saved animation reload validation" % report["status"])
    print("JSON report: %s" % report_path)
    if report["status"] != "PASS":
        raise RuntimeError("Saved technical animation validation failed")


if __name__ == "__main__":
    main()
