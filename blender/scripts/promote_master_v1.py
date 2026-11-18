"""Promote the owner-approved TASK-0007A rc.3 to canonical Master Avatar v1.0.0."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import CORE_NMM, TECHNICAL_ACTIONS, inventory, neutral_state, same_release_structure, write_json


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def clear_assignments_keep_actions():
    changed = []
    ids = list(bpy.data.objects)
    ids.extend(mesh.shape_keys for mesh in bpy.data.meshes if mesh.shape_keys)
    for data_block in ids:
        animation = getattr(data_block, "animation_data", None)
        if animation:
            if animation.action is not None:
                animation.action = None
                changed.append(getattr(data_block, "name", repr(data_block)))
            for track in list(animation.nla_tracks):
                animation.nla_tracks.remove(track)
                changed.append(getattr(data_block, "name", repr(data_block)))
    return sorted(set(changed))


def main():
    args = arguments()
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError(f"Expected Blender {args.expected_version}, got {bpy.app.version_string}")

    source_path = Path(bpy.data.filepath).resolve()
    source_hash_before = sha256(source_path)
    if source_hash_before != args.expected_source_sha256.upper():
        raise RuntimeError("Approved rc.3 source hash mismatch")
    if bpy.context.scene.get("master_avatar_version") != "1.0.0-rc.3":
        raise RuntimeError("Approved source is not Master Avatar v1.0.0-rc.3")

    before = inventory()
    if before["bone_count"] != 137:
        raise RuntimeError("Expected 137 bones")
    if set(before["core_nmm_targets"]) != set(CORE_NMM):
        raise RuntimeError("Six core NMM Morph Targets are required")
    missing_actions = [name for name in TECHNICAL_ACTIONS if name not in before["actions"]]
    if missing_actions:
        raise RuntimeError("Missing technical Actions: " + ", ".join(missing_actions))

    scene = bpy.context.scene
    scene.frame_set(1)
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 1
    body = bpy.data.objects["Human"]
    for name in CORE_NMM:
        body.data.shape_keys.key_blocks[name].value = 0.0
    armature = bpy.data.objects["Human.rig"]
    for pose_bone in armature.pose.bones:
        pose_bone.matrix_basis = Matrix.Identity(4)
    cleared_assignments = clear_assignments_keep_actions()
    scene.frame_set(1)

    for name in TECHNICAL_ACTIONS:
        action = bpy.data.actions[name]
        action.use_fake_user = True
        action["technical_fixture_only"] = True
        action["linguistic_status"] = "NOT YET TESTED"
    scene["master_avatar_name"] = "Master Avatar v1.0.0"
    scene["master_avatar_version"] = "1.0.0"
    scene["release_status"] = "Temporary Technical Release"
    scene["owner_visual_approval"] = "APPROVED"
    scene["technical_validation"] = "PENDING POST-SAVE VALIDATION"
    scene["linguistic_approval"] = "NOT YET TESTED"
    scene["source_candidate_sha256"] = source_hash_before
    scene["technical_actions_are_fixtures"] = True

    bpy.context.view_layer.update()
    after = inventory()
    structure_unchanged = same_release_structure(before, after)
    if not structure_unchanged:
        raise RuntimeError("Release neutralization changed approved structure or geometry")

    neutral = neutral_state()
    neutral_ok = (
        neutral["frame_current"] == 1
        and neutral["fps"] == 30
        and neutral["frame_start"] == 1
        and neutral["frame_end"] == 1
        and not neutral["pose_non_identity"]
        and not neutral["animation_assignments"]
        and all(abs(value) <= 1e-8 for value in neutral["nmm_values"].values())
    )
    if not neutral_ok:
        raise RuntimeError("Canonical neutral state validation failed before save")

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    result = bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, check_existing=False)
    if result != {"FINISHED"} or not output.exists():
        raise RuntimeError("Unable to save canonical master")

    source_hash_after = sha256(source_path)
    report = {
        "schema_version": 1,
        "artifact": "master_avatar_v1_promotion",
        "status": "PASS" if source_hash_before == source_hash_after else "FAIL",
        "blender_version": bpy.app.version_string,
        "mpfb_version": "2.0.18",
        "release": {
            "name": "Master Avatar v1.0.0",
            "version": "1.0.0",
            "classification": "Temporary Technical Release",
            "owner_visual_approval": "APPROVED",
            "linguistic_approval": "NOT YET TESTED",
        },
        "source_candidate": {
            "path": str(source_path),
            "sha256_before": source_hash_before,
            "sha256_after": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
        },
        "canonical_master": {
            "path": str(output),
            "sha256": sha256(output),
            "size_bytes": output.stat().st_size,
        },
        "inventory_before": before,
        "inventory_after": after,
        "structure_and_geometry_unchanged": structure_unchanged,
        "neutral_state": neutral,
        "cleared_runtime_assignments": cleared_assignments,
        "retained_technical_actions": list(TECHNICAL_ACTIONS),
    }
    write_json(args.report, report)
    print(f"{report['status']} Master Avatar v1 promotion: {output}")
    if report["status"] != "PASS":
        raise RuntimeError("Approved source changed during promotion")


if __name__ == "__main__":
    main()
