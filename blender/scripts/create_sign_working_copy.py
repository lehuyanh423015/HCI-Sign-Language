"""Create an isolated sign-animation working file from Master Avatar v1.0.0.

Run with Blender 5.2.4 and the canonical master passed before ``--python``.
The script refuses to overwrite the canonical source or an existing output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import CORE_NMM, inventory, neutral_state, write_json

EXPECTED_MASTER_SHA256 = "DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC"
EXPECTED_HIERARCHY_SHA256 = "0A14E14E5899D4697732D0B0E3F6AC1D6531979B87A7CD23E2652865D9DC2F89"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign-id", required=True, help="S001-S999, or TEMPLATE")
    parser.add_argument("--output", required=True)
    parser.add_argument("--report")
    parser.add_argument("--frame-end", type=int, default=120)
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def clear_runtime_assignments():
    data_blocks = list(bpy.data.objects)
    data_blocks.extend(mesh.shape_keys for mesh in bpy.data.meshes if mesh.shape_keys)
    for data_block in data_blocks:
        animation = getattr(data_block, "animation_data", None)
        if not animation:
            continue
        animation.action = None
        for track in list(animation.nla_tracks):
            animation.nla_tracks.remove(track)


def establish_neutral():
    clear_runtime_assignments()
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or body is None:
        raise RuntimeError("Human/Human.rig missing")
    for bone in armature.pose.bones:
        bone.location = (0.0, 0.0, 0.0)
        bone.rotation_mode = "QUATERNION"
        bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        bone.scale = (1.0, 1.0, 1.0)
    for mesh in bpy.data.meshes:
        if not mesh.shape_keys:
            continue
        for key in mesh.shape_keys.key_blocks:
            if key.name.startswith("NMM_"):
                key.value = 0.0
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()


def ensure_collections():
    scene_collection = bpy.context.scene.collection
    for name, purpose in (
        ("SIGN_ANIMATION_GUIDES", "Animator-only guides; exclude from export."),
        ("SIGN_EXPORT_NOTES", "Non-rendering production notes; exclude from export."),
    ):
        collection = bpy.data.collections.get(name) or bpy.data.collections.new(name)
        collection["purpose"] = purpose
        if collection.name not in {child.name for child in scene_collection.children}:
            scene_collection.children.link(collection)


def main():
    args = arguments()
    sign_id = args.sign_id.upper()
    allowed_fixture = sign_id == "TECHNICAL_FIXTURE_NOT_A_SIGN"
    if sign_id != "TEMPLATE" and not allowed_fixture and not re.fullmatch(r"S\d{3}", sign_id):
        raise RuntimeError("--sign-id must be Snnn, TEMPLATE, or TECHNICAL_FIXTURE_NOT_A_SIGN")
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError(f"Expected Blender {args.expected_version}, got {bpy.app.version_string}")
    source = Path(bpy.data.filepath).resolve()
    output = Path(args.output).resolve()
    if source == output:
        raise RuntimeError("Refusing to overwrite the canonical master")
    if output.exists():
        raise RuntimeError(f"Refusing to overwrite existing working file: {output}")
    source_hash = sha256(source)
    if source_hash != EXPECTED_MASTER_SHA256:
        raise RuntimeError(f"Canonical master SHA-256 mismatch: {source_hash}")
    before = inventory()
    if before["bone_count"] != 137 or before["hierarchy_sha256"] != EXPECTED_HIERARCHY_SHA256:
        raise RuntimeError("Canonical master hierarchy does not match v1.0.0")
    if set(before["core_nmm_targets"]) != set(CORE_NMM):
        raise RuntimeError("Canonical master does not contain the six core NMM targets")

    establish_neutral()
    ensure_collections()
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = args.frame_end
    scene["sign_id"] = sign_id
    scene["sign_pipeline_status"] = "TEMPLATE" if sign_id == "TEMPLATE" else "TECHNICAL_FIXTURE" if allowed_fixture else "IN_PRODUCTION"
    scene["source_master_version"] = "1.0.0"
    scene["source_master_sha256"] = EXPECTED_MASTER_SHA256
    scene["linguistic_review_status"] = "NOT YET TESTED"
    scene["technical_review_status"] = "NOT YET TESTED"
    after = inventory()
    if before != after:
        raise RuntimeError("Working-copy preparation changed the release inventory")
    state = neutral_state()
    if state["pose_non_identity"] or state["animation_assignments"] or any(abs(value) > 1e-8 for value in state["nmm_values"].values()):
        raise RuntimeError("Working copy is not neutral")

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    payload = {
        "schema_version": 1,
        "artifact": "sign_animation_working_copy",
        "status": "PASS",
        "sign_id": sign_id,
        "blender_version": bpy.app.version_string,
        "source": {"path": str(source), "sha256": source_hash, "version": "1.0.0"},
        "output": {"path": str(output), "sha256": sha256(output)},
        "inventory": after,
        "neutral_state": state,
        "canonical_overwrite_prevented": source != output,
        "linguistic_status": "NOT YET TESTED",
    }
    if args.report:
        write_json(args.report, payload)
    print(f"PASS sign working copy: {sign_id} -> {output}")


if __name__ == "__main__":
    main()
