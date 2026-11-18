"""Validate the promoted Master Avatar v1 source in Blender 5.2.4."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import CORE_NMM, EYE_OBJECTS, TECHNICAL_ACTIONS, inventory, neutral_state, write_json


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--promotion-report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def main():
    args = arguments()
    promotion = json.loads(Path(args.promotion_report).read_text(encoding="utf-8"))
    current = inventory()
    expected = promotion["inventory_after"]
    neutral = neutral_state()
    armature = bpy.data.objects.get("Human.rig")

    checks = []
    add = lambda check_id, passed, actual: checks.append({
        "id": check_id, "status": "PASS" if passed else "FAIL", "actual": actual,
    })
    add("blender_version", bpy.app.version_string.startswith(args.expected_version), bpy.app.version_string)
    add("canonical_sha256", sha256(bpy.data.filepath) == promotion["canonical_master"]["sha256"], sha256(bpy.data.filepath))
    add("release_version", bpy.context.scene.get("master_avatar_version") == "1.0.0", bpy.context.scene.get("master_avatar_version"))
    add("release_status", bpy.context.scene.get("release_status") == "Temporary Technical Release", bpy.context.scene.get("release_status"))
    add("owner_visual_approval", bpy.context.scene.get("owner_visual_approval") == "APPROVED", bpy.context.scene.get("owner_visual_approval"))
    add("linguistic_approval", bpy.context.scene.get("linguistic_approval") == "NOT YET TESTED", bpy.context.scene.get("linguistic_approval"))
    add("bone_count", current["bone_count"] == 137, current["bone_count"])
    add("deform_bone_count", current["deform_bone_count"] == expected["deform_bone_count"], current["deform_bone_count"])
    add("hierarchy", current["hierarchy_sha256"] == expected["hierarchy_sha256"], current["hierarchy_sha256"])
    add("geometry", current["geometry_sha256"] == expected["geometry_sha256"], current["geometry_sha256"])
    add("mesh_armature_bindings", current["binding_sha256"] == expected["binding_sha256"], current["binding_sha256"])
    add("object_transforms", current["object_transform_sha256"] == expected["object_transform_sha256"], current["object_transform_sha256"])
    add("six_core_nmm_targets", set(current["core_nmm_targets"]) == set(CORE_NMM), current["core_nmm_targets"])
    add("eye_geometry", set(current["eye_objects"]) == set(EYE_OBJECTS), current["eye_objects"])
    add("technical_actions", all(name in current["actions"] for name in TECHNICAL_ACTIONS), current["actions"])
    add("technical_action_curves", current["technical_action_sha256"] == expected["technical_action_sha256"], current["technical_action_sha256"])
    add("neutral_nmm_values", all(abs(value) <= 1e-8 for value in neutral["nmm_values"].values()), neutral["nmm_values"])
    add("neutral_pose", not neutral["pose_non_identity"], neutral["pose_non_identity"])
    add("no_assigned_animation", not neutral["animation_assignments"], neutral["animation_assignments"])
    add("neutral_timeline", neutral["frame_current"] == 1 and neutral["frame_start"] == 1 and neutral["frame_end"] == 1 and neutral["fps"] == 30, neutral)

    for side in ("L", "R"):
        for finger_index in range(1, 6):
            expected_chain = [f"finger{finger_index}-{segment}.{side}" for segment in range(1, 4)]
            matches = [name for name in expected_chain if armature.data.bones.get(name) is not None]
            add(f"finger_chain_{finger_index}_{side}", matches == expected_chain, matches)

    eye_binding = {}
    for name in EYE_OBJECTS:
        obj = bpy.data.objects.get(name)
        side = "L" if name.endswith(".L") else "R"
        group = obj.vertex_groups.get(f"eye.{side}") if obj else None
        modifiers = [mod.object.name for mod in obj.modifiers if mod.type == "ARMATURE" and mod.object] if obj else []
        fully_weighted = bool(obj and group) and all(
            any(item.group == group.index and abs(float(item.weight) - 1.0) < 1e-6 for item in vertex.groups)
            for vertex in obj.data.vertices
        )
        eye_binding[name] = {"armature_modifiers": modifiers, "fully_weighted": fully_weighted}
    add("eye_bindings", all(row["armature_modifiers"] == ["Human.rig"] and row["fully_weighted"] for row in eye_binding.values()), eye_binding)

    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "schema_version": 1,
        "artifact": "master_avatar_v1_blender_validation",
        "status": status,
        "technical_validation": status,
        "owner_visual_approval": "APPROVED",
        "linguistic_approval": "NOT YET TESTED",
        "source": {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)},
        "inventory": current,
        "neutral_state": neutral,
        "checks": checks,
    }
    write_json(args.output, report)
    for item in checks:
        print(f"{item['status']} Master Avatar v1: {item['id']}")
    print(f"{status} Master Avatar v1 Blender validation")
    if status != "PASS":
        raise RuntimeError("Master Avatar v1 Blender validation failed")


if __name__ == "__main__":
    main()
