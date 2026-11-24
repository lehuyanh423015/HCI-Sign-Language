"""Validate a Master Avatar v1 sign working file without granting content approval."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import CORE_NMM, inventory, neutral_state, write_json

MASTER_SHA256 = "DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC"
HIERARCHY_SHA256 = "0A14E14E5899D4697732D0B0E3F6AC1D6531979B87A7CD23E2652865D9DC2F89"
BINDING_SHA256 = "2AB953B2DE41A87BDB8C8AFFC408647236A18DAFDA3CA140011679A495D2F2C5"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign-id", required=True)
    parser.add_argument("--expected-clip")
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def main():
    args = arguments()
    current = inventory()
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    neutral = neutral_state()
    expected_clip = args.expected_clip or (f"{args.sign_id}_MAIN" if args.sign_id.startswith("S") else None)
    is_fixture = args.sign_id in {"TECHNICAL_FIXTURE_NOT_A_SIGN", "TECH_POSE_AUTHORING_PILOT"}
    is_sign = args.sign_id.startswith("S")
    action = bpy.data.actions.get(expected_clip) if expected_clip else None
    checks = []

    def add(check_id, passed, actual, pending=False):
        checks.append({"id": check_id, "status": "NOT YET TESTED" if pending else "PASS" if passed else "FAIL", "actual": actual})

    add("blender_version", bpy.app.version_string == args.expected_version, bpy.app.version_string)
    add("source_master_version", scene.get("source_master_version") == "1.0.0", scene.get("source_master_version"))
    add("source_master_sha256", scene.get("source_master_sha256") == MASTER_SHA256, scene.get("source_master_sha256"))
    add("sign_id", scene.get("sign_id") == args.sign_id, scene.get("sign_id"))
    add("bone_count", current["bone_count"] == 137, current["bone_count"])
    add("hierarchy", current["hierarchy_sha256"] == HIERARCHY_SHA256, current["hierarchy_sha256"])
    add("mesh_armature_bindings", current["binding_sha256"] == BINDING_SHA256, current["binding_sha256"])
    add("six_core_nmm_targets", set(current["core_nmm_targets"]) == set(CORE_NMM), current["core_nmm_targets"])
    add("fps", scene.render.fps == 30, scene.render.fps)
    add("valid_timeline", scene.frame_start == 1 and scene.frame_end > scene.frame_start, [scene.frame_start, scene.frame_end])
    add("neutral_pose_at_frame_1", not neutral["pose_non_identity"], neutral["pose_non_identity"])
    add("neutral_nmm_at_frame_1", all(abs(value) <= 1e-8 for value in neutral["nmm_values"].values()), neutral["nmm_values"])
    add("expected_action", action is not None, expected_clip, pending=expected_clip is None)
    if action:
        add("positive_action_range", action.frame_range[1] > action.frame_range[0], list(action.frame_range))
    if is_fixture:
        checks.append({"id": "linguistic_review", "status": "NOT_APPLICABLE", "actual": scene.get("linguistic_review_status")})
    else:
        add("linguistic_review", False, scene.get("linguistic_review_status", "NOT YET TESTED"), pending=True)
    status = "FAIL" if any(item["status"] == "FAIL" for item in checks) else "PASS"
    report = {
        "schema_version": 1,
        "artifact": "sign_animation_blender_validation",
        "status": status,
        "technical_validation": status,
        "linguistic_validation": "NOT_APPLICABLE" if is_fixture else "NOT YET TESTED",
        "classification": "TECHNICAL_FIXTURE_NOT_A_SIGN" if not is_sign else "SIGN_PRODUCTION_CANDIDATE",
        "source": {"path": bpy.data.filepath, "sha256": hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest().upper()},
        "inventory": current,
        "neutral_state": neutral,
        "checks": checks,
    }
    write_json(args.output, report)
    for item in checks:
        print(f"{item['status']} sign animation: {item['id']}")
    if status != "PASS":
        raise RuntimeError("Sign animation validation failed")


if __name__ == "__main__":
    main()
