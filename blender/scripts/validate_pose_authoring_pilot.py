"""Validate the generated TECH_POSE_AUTHORING_PILOT source in Blender."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import CORE_NMM, inventory, write_json
from rig_control_utils import action_fcurves, evaluated_mesh_vertices, mesh_delta, sha256
from sign_pose_utils import all_hand_bones, identity_matrix_values, require_armature, require_pose_bone


ACTION_NAME = "TECH_POSE_AUTHORING_PILOT"
EXPECTED_HIERARCHY = "0A14E14E5899D4697732D0B0E3F6AC1D6531979B87A7CD23E2652865D9DC2F89"
EXPECTED_BINDING = "2AB953B2DE41A87BDB8C8AFFC408647236A18DAFDA3CA140011679A495D2F2C5"
EXPECTED_TRANSFORMS = "2FF1F56AC998DB52EB6B9E275F642C7FF279CAE486E40597189662048AD2A5A5"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def bone_name_from_path(path):
    marker = 'pose.bones["'
    return path.split(marker, 1)[1].split('"]', 1)[0] if marker in path else None


def frame_state(scene, armature, body, frame, bone_names):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    return {
        "frame": frame,
        "neutral_bones": [name for name in bone_names if identity_matrix_values(require_pose_bone(armature, name).matrix_basis)],
        "changed_bones": [name for name in bone_names if not identity_matrix_values(require_pose_bone(armature, name).matrix_basis)],
        "morphs": {name: float(body.data.shape_keys.key_blocks[name].value) for name in CORE_NMM},
    }


def main():
    args = arguments()
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    current = inventory()
    armature, body = require_armature()
    scene = bpy.context.scene
    action = bpy.data.actions.get(ACTION_NAME)
    checks = []

    def add(check_id, passed, actual, status=None):
        checks.append({"id": check_id, "status": status or ("PASS" if passed else "FAIL"), "actual": actual})

    add("master_version", scene.get("source_master_version") == "1.0.0", scene.get("source_master_version"))
    add("fixture_identifier", scene.get("sign_id") == ACTION_NAME, scene.get("sign_id"))
    add("bone_count", current["bone_count"] == 137, current["bone_count"])
    add("hierarchy", current["hierarchy_sha256"] == EXPECTED_HIERARCHY, current["hierarchy_sha256"])
    add("mesh_armature_bindings", current["binding_sha256"] == EXPECTED_BINDING, current["binding_sha256"])
    add("object_transforms", current["object_transform_sha256"] == EXPECTED_TRANSFORMS, current["object_transform_sha256"])
    add("six_core_nmm_targets", set(current["core_nmm_targets"]) == set(CORE_NMM), current["core_nmm_targets"])
    add("expected_action", action is not None, ACTION_NAME)
    if action is None:
        write_json(args.output, {"schema_version": 1, "artifact": "pose_authoring_pilot_validation", "status": "FAIL", "checks": checks})
        raise RuntimeError("Expected action missing")

    object_slot = next((slot for slot in action.slots if slot.target_id_type == "OBJECT"), None)
    key_slot = next((slot for slot in action.slots if slot.target_id_type == "KEY"), None)
    object_curves = list(action_fcurves(action, object_slot)) if object_slot else []
    key_curves = list(action_fcurves(action, key_slot)) if key_slot else []
    animated_bones = sorted({name for curve in object_curves if (name := bone_name_from_path(curve.data_path))})
    expected_bones = set(all_hand_bones("L") + all_hand_bones("R") + [
        "wrist.L", "wrist.R", "upperarm01.L", "upperarm01.R",
        "lowerarm01.L", "lowerarm01.R", "head", "neck02", "jaw",
    ])
    add("action_slots", object_slot is not None and key_slot is not None, {"object": object_slot.identifier if object_slot else None, "key": key_slot.identifier if key_slot else None})
    add("action_frame_range", list(action.frame_range) == [1.0, 60.0], list(action.frame_range))
    add("positive_keyframes", sum(len(curve.keyframe_points) for curve in object_curves + key_curves) > 0, sum(len(curve.keyframe_points) for curve in object_curves + key_curves))
    add("expected_bone_channels", set(animated_bones) == expected_bones, {"actual": animated_bones, "missing": sorted(expected_bones - set(animated_bones)), "unexpected": sorted(set(animated_bones) - expected_bones)})
    weight_paths = sorted({curve.data_path for curve in key_curves})
    add("morph_channels", len(key_curves) == len(CORE_NMM) and all("key_blocks" in path for path in weight_paths), weight_paths)

    states = {frame: frame_state(scene, armature, body, frame, sorted(expected_bones)) for frame in (1, 12, 24, 36, 48, 60)}
    for frame in (1, 60):
        neutral = not states[frame]["changed_bones"] and all(abs(value) <= 1e-6 for value in states[frame]["morphs"].values())
        add("neutral_reset_frame_%d" % frame, neutral, states[frame])
    left_hand = set(all_hand_bones("L"))
    right_hand = set(all_hand_bones("R"))
    add("right_hand_independent_frame_12", not (left_hand & set(states[12]["changed_bones"])) and bool(right_hand & set(states[12]["changed_bones"])), states[12])
    add("left_hand_control_frame_36", bool(left_hand & set(states[36]["changed_bones"])), states[36])
    add("both_hands_frame_48", bool(left_hand & set(states[48]["changed_bones"])) and bool(right_hand & set(states[48]["changed_bones"])), states[48])
    add("bone_and_morph_coexist", bool(states[48]["changed_bones"]) and any(value > 0 for value in states[48]["morphs"].values()), states[48])

    scene.frame_set(1)
    neutral_vertices = evaluated_mesh_vertices(body)
    deformation = {}
    for frame in (24, 36, 48):
        scene.frame_set(frame)
        vertices = evaluated_mesh_vertices(body)
        row = mesh_delta(neutral_vertices, vertices)
        row["all_finite"] = all(math.isfinite(component) for point in vertices for component in point)
        deformation[str(frame)] = row
    add("mesh_deformation_present", all(row["moved_vertices"] > 0 for row in deformation.values()), deformation)
    add("mesh_coordinates_finite", all(row["all_finite"] for row in deformation.values()), deformation)
    add("deformation_sanity_bound", all(row["max_distance"] < 0.5 for row in deformation.values()), deformation)

    eye_rows = {}
    for name in ("NMM_Eyeball.L", "NMM_Iris.L", "NMM_Pupil.L", "NMM_Eyeball.R", "NMM_Iris.R", "NMM_Pupil.R"):
        obj = bpy.data.objects.get(name)
        eye_rows[name] = {
            "exists": obj is not None,
            "armature": [mod.object.name for mod in obj.modifiers if mod.type == "ARMATURE" and mod.object] if obj else [],
        }
    add("eye_mesh_bindings", all(row["exists"] and row["armature"] == ["Human.rig"] for row in eye_rows.values()), eye_rows)
    add("visual_anatomical_quality", False, "See generated renders and MP4; owner review required.", status="NOT YET TESTED")
    add("linguistic_review", False, "NOT_APPLICABLE technical fixture; real sign pilot BLOCKED.", status="NOT_APPLICABLE")

    status = "FAIL" if any(item["status"] == "FAIL" for item in checks) else "PASS"
    report = {
        "schema_version": 1,
        "artifact": "pose_authoring_pilot_validation",
        "status": status,
        "classification": "TECHNICAL_FIXTURE_NOT_A_SIGN",
        "linguistic_status": "NOT_APPLICABLE",
        "source": {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)},
        "build_report": str(Path(args.build_report).resolve()),
        "action": {"name": ACTION_NAME, "animated_bones": animated_bones, "object_fcurves": len(object_curves), "morph_fcurves": len(key_curves)},
        "frame_states": states,
        "deformation": deformation,
        "checks": checks,
    }
    write_json(args.output, report)
    for item in checks:
        print("%s pose pilot: %s" % (item["status"], item["id"]))
    if status != "PASS":
        raise RuntimeError("Pose authoring pilot validation failed")


if __name__ == "__main__":
    main()
