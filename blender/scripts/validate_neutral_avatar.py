"""Reload and validate the neutral avatar, rig binding, coverage and animation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import (
    TECHNICAL_BONES,
    action_fcurves,
    evaluated_mesh_vertices,
    matrix_signature,
    mesh_delta,
    require_rig,
    sha256,
)


ACTION_NAME = "TECH_HAND_CONTROL_TEST"
GARMENT_NAMES = ("EDU_NeutralTop", "EDU_NeutralShorts")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def bounds(obj):
    points = [vertex.co for vertex in obj.data.vertices]
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


def bound_to_armature(obj, armature):
    modifiers = [modifier for modifier in obj.modifiers if modifier.type == "ARMATURE"]
    return obj.parent == armature and len(modifiers) == 1 and modifiers[0].object == armature


def main():
    args = arguments()
    armature, body = require_rig()
    garments = [bpy.data.objects.get(name) for name in GARMENT_NAMES]
    action = bpy.data.actions.get(ACTION_NAME)
    slot = next((item for item in action.slots if item.target_id_type == "OBJECT"), None) if action else None
    curves = list(action_fcurves(action, slot)) if action and slot else []
    animated_bones = sorted(
        {
            curve.data_path.split('pose.bones["', 1)[1].split('"]', 1)[0]
            for curve in curves
            if 'pose.bones["' in curve.data_path
        }
    )
    frames = sorted({round(point.co.x, 6) for curve in curves for point in curve.keyframe_points})

    object_transform = matrix_signature(armature.matrix_world)
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    open_vertices = evaluated_mesh_vertices(body)
    bpy.context.scene.frame_set(30)
    bpy.context.view_layer.update()
    closed_vertices = evaluated_mesh_vertices(body)
    deformation = mesh_delta(open_vertices, closed_vertices)
    transform_after = matrix_signature(armature.matrix_world)
    bpy.context.scene.frame_set(1)

    garment_bounds = {garment.name: bounds(garment) for garment in garments if garment}
    top_bounds = garment_bounds.get(GARMENT_NAMES[0], {})
    shorts_bounds = garment_bounds.get(GARMENT_NAMES[1], {})
    checks = {
        "rig_hierarchy_expected": len(armature.data.bones) == 137 and all(name in armature.data.bones for name in TECHNICAL_BONES),
        "body_armature_binding": bound_to_armature(body, armature),
        "garments_present": all(garments),
        "garments_armature_binding": all(bound_to_armature(garment, armature) for garment in garments if garment),
        "garments_weighted": all(all(vertex.groups for vertex in garment.data.vertices) for garment in garments if garment),
        "neutral_materials": body.active_material is not None
        and body.active_material.name == "EDU_Skin_Neutral"
        and [garment.active_material.name for garment in garments if garment]
        == ["EDU_Top_Teal", "EDU_Shorts_Slate"],
        "upper_coverage_bounds": bool(top_bounds)
        and top_bounds["min"][2] <= 0.98
        and top_bounds["max"][2] >= 1.40,
        "lower_coverage_bounds": bool(shorts_bounds)
        and shorts_bounds["min"][2] <= 0.621
        and shorts_bounds["max"][2] >= 1.029
        and shorts_bounds["min"][1] <= -0.20
        and shorts_bounds["max"][1] >= 0.15,
        "technical_action_assigned": action is not None and armature.animation_data is not None and armature.animation_data.action == action,
        "technical_action_shape": len(curves) == 45
        and sum(len(curve.keyframe_points) for curve in curves) == 135
        and frames == [1.0, 15.0, 30.0]
        and animated_bones == sorted(TECHNICAL_BONES),
        "finger_deformation_present": deformation["moved_vertices"] > 0 and deformation["max_distance"] > 0,
        "armature_object_transform_stable": object_transform == transform_after,
        "scene_timing": bpy.context.scene.render.fps == 30 and bpy.context.scene.frame_start == 1 and bpy.context.scene.frame_end == 30,
    }
    report = {
        "schema_version": 1,
        "artifact": "neutral_avatar_reload_validation",
        "source_blend": bpy.data.filepath,
        "source_sha256": sha256(bpy.data.filepath),
        "blender_version": bpy.app.version_string,
        "objects": {
            "body": body.name,
            "armature": armature.name,
            "garments": [garment.name for garment in garments if garment],
        },
        "garment_bounds_local": garment_bounds,
        "animation": {
            "name": action.name if action else None,
            "fcurve_count": len(curves),
            "keyframe_point_count": sum(len(curve.keyframe_points) for curve in curves),
            "frames": frames,
            "animated_bones": animated_bones,
            "body_mesh_delta_frame_1_to_30": deformation,
        },
        "checks": checks,
        "automated_status": "PASS" if all(checks.values()) else "FAIL",
        "human_visual_status": "NOT YET TESTED",
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print("[%s] %s" % ("PASS" if passed else "FAIL", name))
    print("[%s] neutral avatar reload validation" % report["automated_status"])
    print("JSON report: %s" % report_path)
    if report["automated_status"] != "PASS":
        raise RuntimeError("Neutral avatar validation failed")


if __name__ == "__main__":
    main()
