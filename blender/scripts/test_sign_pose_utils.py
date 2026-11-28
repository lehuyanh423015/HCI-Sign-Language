"""Programmatic tests for reusable pose-authoring utilities."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import write_json
from rig_control_utils import evaluated_mesh_vertices, mesh_delta
from sign_pose_utils import (
    PoseAuthor, PoseAuthoringError, all_hand_bones, identity_matrix_values,
    load_pose_library, require_armature, require_pose_bone, reset_full_pose,
    reset_hand, validate_canonical_rig,
)


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pose-library", required=True)
    parser.add_argument("--output", required=True)
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def main():
    args = arguments()
    current = validate_canonical_rig()
    armature, body = require_armature()
    library = load_pose_library(args.pose_library)
    author = PoseAuthor(armature, body)
    checks = []

    def add(check_id, passed, actual):
        checks.append({"id": check_id, "status": "PASS" if passed else "FAIL", "actual": actual})

    expected_poses = {"neutral_hand", "open_hand", "closed_fist", "index_flexed", "thumb_flexed", "relaxed_hand"}
    add("pose_library_loading", expected_poses.issubset(library["poses"]), sorted(library["poses"]))

    invalid_error = None
    try:
        require_pose_bone(armature, "not-a-real-bone")
    except PoseAuthoringError as error:
        invalid_error = str(error)
    add("invalid_bone_handling", bool(invalid_error and "Invalid bone name" in invalid_error), invalid_error)

    reset_full_pose(armature, body)
    baseline_vertices = evaluated_mesh_vertices(body)
    right_affected = author.apply_named_hand_pose("R", "closed_fist", library)
    right_vertices = evaluated_mesh_vertices(body)
    right_delta = mesh_delta(baseline_vertices, right_vertices)
    left_stable = all(identity_matrix_values(require_pose_bone(armature, name).matrix_basis) for name in all_hand_bones("L"))
    right_changed = any(not identity_matrix_values(require_pose_bone(armature, name).matrix_basis) for name in right_affected)
    add("right_hand_independent_control", left_stable and right_changed and right_delta["moved_vertices"] > 0, {"left_stable": left_stable, "right_changed": right_changed, "mesh_delta": right_delta})

    reset_hand(armature, "R")
    reset_vertices = evaluated_mesh_vertices(body)
    reset_delta = mesh_delta(baseline_vertices, reset_vertices)
    add("right_hand_reset", reset_delta["max_distance"] <= 1e-6 and all(identity_matrix_values(require_pose_bone(armature, name).matrix_basis) for name in right_affected), reset_delta)

    left_affected = author.apply_named_hand_pose("L", "index_flexed", library)
    left_vertices = evaluated_mesh_vertices(body)
    left_delta = mesh_delta(baseline_vertices, left_vertices)
    right_stable = all(identity_matrix_values(require_pose_bone(armature, name).matrix_basis) for name in all_hand_bones("R"))
    left_changed = any(not identity_matrix_values(require_pose_bone(armature, name).matrix_basis) for name in left_affected)
    add("left_hand_independent_control", right_stable and left_changed and left_delta["moved_vertices"] > 0, {"right_stable": right_stable, "left_changed": left_changed, "mesh_delta": left_delta})

    reset_full_pose(armature, body)
    author.apply_named_hand_pose("L", "relaxed_hand", library, {"finger2-1": 11}, {"finger2-1": -6})
    author.apply_named_hand_pose("R", "relaxed_hand", library, {"finger2-1": 11}, {"finger2-1": 6})
    left_index = require_pose_bone(armature, "finger2-1.L")
    right_index = require_pose_bone(armature, "finger2-1.R")
    from math import degrees
    adduction_actual = {
        "L_x_flex": round(degrees(left_index.rotation_euler.x), 3),
        "L_z_adduction": round(degrees(left_index.rotation_euler.z), 3),
        "R_x_flex": round(degrees(right_index.rotation_euler.x), 3),
        "R_z_adduction": round(degrees(right_index.rotation_euler.z), 3),
    }
    add("proximal_finger_adduction_independent_of_flexion",
        author.axis_map["finger2-1.L"]["axis"] == "X"
        and author.axis_map["finger2-1.R"]["axis"] == "X"
        and abs(adduction_actual["L_x_flex"]) == 11
        and abs(adduction_actual["R_x_flex"]) == 11
        and adduction_actual["L_z_adduction"] == -6
        and adduction_actual["R_z_adduction"] == 6,
        adduction_actual)

    reset_full_pose(armature, body)
    final_vertices = evaluated_mesh_vertices(body)
    final_delta = mesh_delta(baseline_vertices, final_vertices)
    all_neutral = all(identity_matrix_values(bone.matrix_basis) for bone in armature.pose.bones)
    add("full_pose_reset", all_neutral and final_delta["max_distance"] <= 1e-6, {"all_neutral": all_neutral, "mesh_delta": final_delta})
    add("canonical_hierarchy", current["bone_count"] == 137, {"bone_count": current["bone_count"], "hierarchy_sha256": current["hierarchy_sha256"]})

    report = {
        "schema_version": 1,
        "artifact": "sign_pose_utils_tests",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "blender_version": bpy.app.version_string,
        "classification": "TECHNICAL_RIG_TEST_NOT_SIGN_LANGUAGE",
        "axis_discovery": author.axis_map,
        "checks": checks,
    }
    write_json(args.output, report)
    for item in checks:
        print("%s pose utils: %s" % (item["status"], item["id"]))
    if report["status"] != "PASS":
        raise RuntimeError("Pose authoring tests failed")


if __name__ == "__main__":
    main()
