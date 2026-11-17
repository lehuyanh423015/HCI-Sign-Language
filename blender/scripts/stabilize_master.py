"""Create the animation-free canonical master from an approved working copy.

This script is intentionally destructive only to the output copy loaded by
Blender. It must never be run with the approved candidate as ``--output``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy


MASTER_VERSION = "1.0.0-rc.1"
EXPECTED_OBJECTS = {"Human", "Human.rig", "EDU_NeutralTop", "EDU_NeutralShorts"}
TECHNICAL_ACTION = "TECH_HAND_CONTROL_TEST"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def sha256(path_value):
    digest = hashlib.sha256()
    with Path(path_value).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def hierarchy_signature(armature):
    rows = [
        "%s|%s|%s" % (bone.name, bone.parent.name if bone.parent else "", int(bone.use_deform))
        for bone in armature.data.bones
    ]
    return hashlib.sha256("\n".join(sorted(rows)).encode("utf-8")).hexdigest().upper()


def main():
    args = arguments()
    source_path = Path(bpy.data.filepath).resolve()
    output_path = Path(args.output).resolve()
    report_path = Path(args.report).resolve()
    if source_path == output_path:
        raise RuntimeError("Refusing to overwrite the loaded source candidate")
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))

    missing = sorted(EXPECTED_OBJECTS - set(bpy.data.objects.keys()))
    if missing:
        raise RuntimeError("Approved neutral objects missing: %s" % ", ".join(missing))
    armature = bpy.data.objects["Human.rig"]
    if armature.type != "ARMATURE" or len(armature.data.bones) != 137:
        raise RuntimeError("Canonical armature must contain exactly 137 bones")

    source = {
        "path": str(source_path),
        "sha256": sha256(source_path),
        "actions": sorted(action.name for action in bpy.data.actions),
        "armature_hierarchy_sha256": hierarchy_signature(armature),
        "armature_rotation_euler": list(armature.rotation_euler),
    }
    if TECHNICAL_ACTION not in source["actions"]:
        raise RuntimeError("Expected technical action %s was not found" % TECHNICAL_ACTION)

    for obj in bpy.data.objects:
        if obj.animation_data:
            obj.animation_data_clear()
    for shape_keys in [mesh.shape_keys for mesh in bpy.data.meshes if mesh.shape_keys]:
        if shape_keys.animation_data:
            shape_keys.animation_data_clear()
    for pose_bone in armature.pose.bones:
        pose_bone.matrix_basis.identity()
    bpy.context.view_layer.update()

    technical_action = bpy.data.actions.get(TECHNICAL_ACTION)
    if technical_action:
        bpy.data.actions.remove(technical_action)
    if bpy.data.actions:
        raise RuntimeError("Unexpected actions remain in canonical master: %s" % ", ".join(bpy.data.actions.keys()))

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 1
    scene.frame_set(1)
    scene["master_avatar_version"] = MASTER_VERSION
    scene["master_avatar_status"] = "release-candidate"
    scene["master_avatar_source_sha256"] = source["sha256"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path), check_existing=False)

    report = {
        "schema_version": 1,
        "operation": "canonical_master_promotion",
        "status": "PASS",
        "master_version": MASTER_VERSION,
        "blender_version": bpy.app.version_string,
        "source": source,
        "output": {
            "path": str(output_path),
            "sha256": sha256(output_path),
            "objects": sorted((obj.name, obj.type) for obj in bpy.data.objects),
            "actions": sorted(action.name for action in bpy.data.actions),
            "fps": scene.render.fps,
            "frame_range": [scene.frame_start, scene.frame_end],
            "bone_count": len(armature.data.bones),
            "armature_hierarchy_sha256": hierarchy_signature(armature),
            "armature_rotation_euler": list(armature.rotation_euler),
            "neutral_pose_basis_identity": all(pose_bone.matrix_basis.is_identity for pose_bone in armature.pose.bones),
        },
        "preservation": {
            "source_was_not_output": source_path != output_path,
            "hierarchy_unchanged": source["armature_hierarchy_sha256"] == hierarchy_signature(armature),
            "armature_object_rotation_retained": source["armature_rotation_euler"] == list(armature.rotation_euler),
            "technical_action_removed_from_output_only": TECHNICAL_ACTION not in bpy.data.actions,
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS canonical master: %s" % output_path)
    print("SHA-256: %s" % report["output"]["sha256"])
    print("JSON report: %s" % report_path)


if __name__ == "__main__":
    main()
