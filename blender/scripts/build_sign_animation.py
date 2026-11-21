"""Build an editable Blender 5.2 Action from a validated motion specification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import CORE_NMM, write_json
from rig_control_utils import action_fcurves, sha256
from sign_pose_utils import PoseAuthor, PoseAuthoringError, load_json, load_pose_library, require_armature, reset_full_pose, validate_canonical_rig


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--pose-library", required=True)
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--overwrite-action", action="store_true")
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def validate_spec_minimum(spec, pose_library):
    if spec.get("schema_version") != 1:
        raise PoseAuthoringError("Unsupported motion spec version")
    identification = spec.get("identification", {})
    if identification.get("fps") != 30 or identification.get("master_version") != "1.0.0":
        raise PoseAuthoringError("Motion spec fps/master version mismatch")
    poses = spec.get("key_poses", [])
    frames = [row.get("frame") for row in poses]
    if len(poses) < 2 or frames != sorted(set(frames)):
        raise PoseAuthoringError("Motion spec key poses must have unique increasing frames")
    if frames[-1] > spec.get("timing", {}).get("duration_frames", 0):
        raise PoseAuthoringError("Motion spec key pose exceeds duration")
    known = set(pose_library.get("poses", {}))
    for row in poses:
        for side in ("left_hand", "right_hand"):
            if row[side]["pose"] not in known:
                raise PoseAuthoringError("Unknown pose in spec: %s" % row[side]["pose"])


def set_interpolation(action, slots, interpolation):
    for slot in slots:
        for curve in action_fcurves(action, slot):
            for point in curve.keyframe_points:
                point.interpolation = interpolation


def main():
    args = arguments()
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    source = Path(bpy.data.filepath).resolve()
    output = Path(args.output_blend).resolve()
    if source == output:
        raise RuntimeError("Refusing to overwrite input working copy")
    if output.exists():
        raise RuntimeError("Refusing to overwrite existing output: %s" % output)
    spec = load_json(args.spec)
    pose_library = load_pose_library(args.pose_library)
    validate_spec_minimum(spec, pose_library)
    current = validate_canonical_rig()
    armature, body = require_armature()
    action_name = spec["identification"]["animation_name"]
    scene_identifier = bpy.context.scene.get("sign_id")
    expected_identifier = spec["identification"].get("sign_id") or spec["identification"].get("fixture_id")
    if scene_identifier != expected_identifier:
        raise RuntimeError("Working copy identifier mismatch: %s != %s" % (scene_identifier, expected_identifier))

    existing = bpy.data.actions.get(action_name)
    if existing and not args.overwrite_action:
        raise RuntimeError("Action already exists; use --overwrite-action explicitly: %s" % action_name)
    if existing:
        bpy.data.actions.remove(existing)
    action = bpy.data.actions.new(action_name)
    object_slot = action.slots.new(id_type="OBJECT", name=armature.name)
    key_slot = action.slots.new(id_type="KEY", name=body.data.shape_keys.name)
    armature_animation = armature.animation_data_create()
    key_animation = body.data.shape_keys.animation_data_create()
    armature_animation.action = action
    armature_animation.action_slot = object_slot
    key_animation.action = action
    key_animation.action_slot = key_slot

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = spec["timing"]["frame_start"]
    scene.frame_end = spec["timing"]["duration_frames"]
    scene["motion_spec"] = str(Path(args.spec).resolve())
    scene["motion_spec_classification"] = spec["classification"]
    scene["linguistic_review_status"] = "NOT_APPLICABLE" if spec["classification"] == "TECHNICAL_FIXTURE_NOT_A_SIGN" else "NOT YET TESTED"

    author = PoseAuthor(armature, body)
    rows = []
    all_animated_bones = set()
    for index, key_pose in enumerate(spec["key_poses"]):
        frame = key_pose["frame"]
        reset_full_pose(armature, body)
        affected = []
        for side_key, side in (("left_hand", "L"), ("right_hand", "R")):
            hand = key_pose[side_key]
            affected.extend(author.apply_named_hand_pose(side, hand["pose"], pose_library, hand.get("finger_overrides")))
            affected.append(author.apply_local_rotation("wrist.%s" % side, hand["wrist_orientation_degrees"]))
            for semantic, degrees in hand["arm_rotations_degrees"].items():
                affected.append(author.apply_local_rotation("%s.%s" % (semantic, side), degrees))
        non_manual = key_pose["non_manual"]
        affected.append(author.apply_local_rotation("head", non_manual["head_orientation_degrees"]))
        affected.append(author.apply_local_rotation("neck02", non_manual["neck_rotation_degrees"]))
        affected.append(author.apply_local_rotation("jaw", [non_manual["jaw_position_degrees"], 0, 0]))
        author.apply_morphs(non_manual["morph_targets"])
        keyed_bones = author.keyframe_bones(affected, frame)
        keyed_morphs = author.keyframe_morphs(frame)
        all_animated_bones.update(keyed_bones)
        hold_frame = min(frame + key_pose.get("hold_frames", 0), scene.frame_end)
        next_frame = spec["key_poses"][index + 1]["frame"] if index + 1 < len(spec["key_poses"]) else None
        if hold_frame > frame and (next_frame is None or hold_frame < next_frame):
            author.keyframe_bones(affected, hold_frame)
            author.keyframe_morphs(hold_frame)
        rows.append({
            "frame": frame,
            "label": key_pose["label"],
            "hold_frame": hold_frame if hold_frame > frame else None,
            "bones": sorted(set(keyed_bones)),
            "morphs": keyed_morphs,
        })

    set_interpolation(action, (object_slot, key_slot), spec["timing"]["interpolation"])
    object_curves = list(action_fcurves(action, object_slot))
    key_curves = list(action_fcurves(action, key_slot))
    evaluation_frames = sorted({row["frame"] for row in spec["key_poses"]})
    evaluations = [author.evaluate(frame, all_animated_bones) for frame in evaluation_frames]
    scene.frame_set(scene.frame_start)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)

    report = {
        "schema_version": 1,
        "artifact": "data_driven_sign_animation_build",
        "status": "PASS" if object_curves and key_curves else "FAIL",
        "classification": spec["classification"],
        "linguistic_status": scene["linguistic_review_status"],
        "blender_version": bpy.app.version_string,
        "source": {"path": str(source), "sha256": sha256(source)},
        "output": {"path": str(output), "sha256": sha256(output)},
        "spec": {"path": str(Path(args.spec).resolve()), "animation_name": action_name},
        "rig": {"bone_count": current["bone_count"], "hierarchy_sha256": current["hierarchy_sha256"]},
        "action": {
            "name": action_name,
            "frame_range": [scene.frame_start, scene.frame_end],
            "fps": scene.render.fps,
            "object_slot": object_slot.identifier,
            "key_slot": key_slot.identifier,
            "object_fcurve_count": len(object_curves),
            "morph_fcurve_count": len(key_curves),
            "keyframe_point_count": sum(len(curve.keyframe_points) for curve in object_curves + key_curves),
            "animated_bones": sorted(all_animated_bones),
            "animated_morphs": list(CORE_NMM),
        },
        "pose_rows": rows,
        "axis_discovery": author.axis_map,
        "evaluations": evaluations,
    }
    write_json(args.report, report)
    print("%s pose animation build: %s (%d bone curves, %d morph curves)" % (report["status"], action_name, len(object_curves), len(key_curves)))
    if report["status"] != "PASS":
        raise RuntimeError("Animation build failed")


if __name__ == "__main__":
    main()
