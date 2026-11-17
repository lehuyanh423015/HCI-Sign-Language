"""Read-only object, mesh, armature, bone and constraint inventory.

Run against a temporary/working copy. This module contains no Blender save,
transform, mode-change, keyframe or animation-creation operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import bpy


VALID_STATUSES = {"PASS", "FAIL", "SKIPPED", "NOT YET TESTED"}
SIDE_PATTERNS = {
    "left": (r"(^|[._\- ])l($|[._\- ])", r"(^|[._\- ])left($|[._\- ])"),
    "right": (r"(^|[._\- ])r($|[._\- ])", r"(^|[._\- ])right($|[._\- ])"),
}
SEMANTIC_ALIASES = {
    "shoulder": ("shoulder", "clavicle", "collar"),
    "elbow": ("elbow", "forearm", "lowerarm", "lower_arm"),
    "wrist": ("wrist", "hand"),
    "thumb": ("thumb", "pollex"),
    "index": ("index", "forefinger"),
    "middle": ("middle",),
    "ring": ("ring",),
    "little": ("little", "pinky", "pinkie"),
}
FINGER_TOKENS = tuple({token for key in ("thumb", "index", "middle", "ring", "little") for token in SEMANTIC_ALIASES[key]}) + ("finger", "digit")


def script_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect an already-loaded rig without changing it.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--expected-version", default=None, help="Optional exact Blender version to record/check.")
    parser.add_argument("--expected-fps", type=int, default=30, help="Project FPS contract.")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def check(check_id: str, status: str, summary: str, critical: bool = False, details=None) -> dict:
    if status not in VALID_STATUSES:
        raise ValueError("Invalid preflight status: %s" % status)
    return {"id": check_id, "status": status, "summary": summary, "critical": critical, "details": details}


def sha256(path_value: str) -> str | None:
    if not path_value or not Path(path_value).is_file():
        return None
    digest = hashlib.sha256()
    with Path(path_value).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def side_of(name: str) -> str | None:
    lowered = name.lower()
    for side, patterns in SIDE_PATTERNS.items():
        if any(re.search(pattern, lowered) for pattern in patterns):
            return side
    return None


def semantic_candidates(bone_names: list[str]) -> dict:
    result = {}
    for semantic, aliases in SEMANTIC_ALIASES.items():
        result[semantic] = {"left": [], "right": [], "unresolved_side": []}
        for name in bone_names:
            lowered = name.lower()
            if not any(alias in lowered for alias in aliases):
                continue
            side = side_of(name)
            result[semantic][side or "unresolved_side"].append(name)
        for candidates in result[semantic].values():
            candidates.sort()
    return result


def constraint_row(constraint) -> dict:
    row = {
        "name": constraint.name,
        "type": constraint.type,
        "influence": constraint.influence,
        "mute": constraint.mute,
        "target": getattr(getattr(constraint, "target", None), "name", None),
        "subtarget": getattr(constraint, "subtarget", None),
    }
    for attribute in ("chain_count", "use_tail", "use_stretch"):
        if hasattr(constraint, attribute):
            row[attribute] = getattr(constraint, attribute)
    return row


def armature_row(armature) -> dict:
    pose_by_name = {bone.name: bone for bone in armature.pose.bones}
    bones = []
    control_bones = []
    all_constraints = []
    for bone in armature.data.bones:
        pose_bone = pose_by_name.get(bone.name)
        constraints = [constraint_row(item) for item in pose_bone.constraints] if pose_bone else []
        custom_shape = getattr(getattr(pose_bone, "custom_shape", None), "name", None) if pose_bone else None
        is_control = (not bone.use_deform) or bool(constraints) or bool(custom_shape) or any(token in bone.name.lower() for token in ("ctrl", "control", "ik", "pole", "target"))
        if is_control:
            control_bones.append(bone.name)
        for item in constraints:
            all_constraints.append({"bone": bone.name, **item})
        bones.append(
            {
                "name": bone.name,
                "parent": bone.parent.name if bone.parent else None,
                "children": sorted(child.name for child in bone.children),
                "use_deform": bone.use_deform,
                "use_connect": bone.use_connect,
                "inherit_scale": bone.inherit_scale,
                "head_local": list(bone.head_local),
                "tail_local": list(bone.tail_local),
                "pose": {
                    "rotation_mode": pose_bone.rotation_mode,
                    "lock_location": list(pose_bone.lock_location),
                    "lock_rotation": list(pose_bone.lock_rotation),
                    "lock_scale": list(pose_bone.lock_scale),
                    "custom_shape": custom_shape,
                    "constraints": constraints,
                } if pose_bone else None,
            }
        )
    names = [row["name"] for row in bones]
    finger_named = sorted(name for name in names if any(token in name.lower() for token in FINGER_TOKENS))
    finger_roots = sorted(
        row["name"] for row in bones
        if any(token in row["name"].lower() for token in FINGER_TOKENS)
        and (not row["parent"] or not any(token in row["parent"].lower() for token in FINGER_TOKENS))
    )
    return {
        "name": armature.name,
        "data_name": armature.data.name,
        "parent": armature.parent.name if armature.parent else None,
        "bone_count": len(bones),
        "deform_bones": sorted(row["name"] for row in bones if row["use_deform"]),
        "control_bones": sorted(control_bones),
        "bones": bones,
        "constraints": all_constraints,
        "ik_constraints": [row for row in all_constraints if row["type"] in {"IK", "SPLINE_IK"}],
        "semantic_candidates": semantic_candidates(names),
        "finger_named_bones": finger_named,
        "finger_chain_roots": finger_roots,
    }


def vertex_group_counts(mesh) -> dict[str, int]:
    counts = {group.name: 0 for group in mesh.vertex_groups}
    names_by_index = {group.index: group.name for group in mesh.vertex_groups}
    for vertex in mesh.data.vertices:
        for membership in vertex.groups:
            name = names_by_index.get(membership.group)
            if name:
                counts[name] += 1
    return counts


def mesh_row(mesh) -> dict:
    counts = vertex_group_counts(mesh)
    modifiers = []
    armature_targets = []
    for modifier in mesh.modifiers:
        row = {"name": modifier.name, "type": modifier.type, "show_viewport": modifier.show_viewport}
        if modifier.type == "ARMATURE":
            target = getattr(getattr(modifier, "object", None), "name", None)
            row.update(
                {
                    "target": target,
                    "use_vertex_groups": getattr(modifier, "use_vertex_groups", None),
                    "use_bone_envelopes": getattr(modifier, "use_bone_envelopes", None),
                }
            )
            if target:
                armature_targets.append(target)
        modifiers.append(row)
    relevant_groups = {
        name: count for name, count in counts.items()
        if any(token in name.lower() for token in FINGER_TOKENS + ("hand", "wrist"))
    }
    return {
        "name": mesh.name,
        "data_name": mesh.data.name,
        "parent": mesh.parent.name if mesh.parent else None,
        "parent_type": mesh.parent_type,
        "vertex_count": len(mesh.data.vertices),
        "edge_count": len(mesh.data.edges),
        "polygon_count": len(mesh.data.polygons),
        "shape_key_count": len(mesh.data.shape_keys.key_blocks) if mesh.data.shape_keys else 0,
        "modifiers": modifiers,
        "armature_targets": sorted(set(armature_targets)),
        "vertex_groups": dict(sorted(counts.items())),
        "hand_vertex_groups": dict(sorted(relevant_groups.items())),
    }


def object_row(obj) -> dict:
    return {
        "name": obj.name,
        "type": obj.type,
        "data_name": getattr(getattr(obj, "data", None), "name", None),
        "parent": obj.parent.name if obj.parent else None,
        "parent_type": obj.parent_type,
        "parent_bone": obj.parent_bone or None,
        "collections": sorted(collection.name for collection in obj.users_collection),
        "location": list(obj.location),
        "rotation_mode": obj.rotation_mode,
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
    }


def snapshot() -> dict:
    return {
        "objects": sorted((obj.name, obj.type) for obj in bpy.data.objects),
        "actions": sorted(action.name for action in bpy.data.actions),
        "armatures": {
            armature.name: sorted((bone.name, bone.parent.name if bone.parent else None) for bone in armature.data.bones)
            for armature in bpy.data.objects if armature.type == "ARMATURE"
        },
    }


def selection_state() -> dict:
    active_object = bpy.context.view_layer.objects.active
    armatures = []
    for armature in sorted((obj for obj in bpy.data.objects if obj.type == "ARMATURE"), key=lambda item: item.name):
        bones = armature.data.bones
        active_bone = getattr(getattr(bones, "active", None), "name", None)
        selected_bones = [bone.name for bone in bones if bool(getattr(bone, "select", False))]
        armatures.append(
            {
                "name": armature.name,
                "object_selected": armature.select_get(),
                "active_bone": active_bone,
                "selected_bones": selected_bones,
            }
        )
    return {
        "mode": bpy.context.mode,
        "active_object": active_object.name if active_object else None,
        "selected_objects": sorted(obj.name for obj in bpy.context.selected_objects),
        "armatures": armatures,
    }


def has_numbered_finger_chains(armature: dict) -> tuple[bool, dict]:
    by_name = {bone["name"]: bone for bone in armature["bones"]}
    details = {}
    complete = True
    for side in ("L", "R"):
        details[side] = {}
        for digit in range(1, 6):
            names = ["finger%d-%d.%s" % (digit, joint, side) for joint in range(1, 4)]
            present = all(name in by_name for name in names)
            linked = present and by_name[names[1]]["parent"] == names[0] and by_name[names[2]]["parent"] == names[1]
            unlocked = present and all(not all(by_name[name]["pose"]["lock_rotation"]) for name in names)
            details[side][str(digit)] = {"bones": names, "present": present, "linked": linked, "rotation_available": unlocked}
            complete = complete and present and linked and unlocked
    return complete, details


def identity_transform_issues(objects: list) -> list[dict]:
    issues = []
    tolerance = 1e-6
    for obj in objects:
        if obj.type != "ARMATURE":
            continue
        location_ok = all(abs(value) <= tolerance for value in obj.location)
        rotation_ok = all(abs(value) <= tolerance for value in obj.rotation_euler)
        scale_ok = all(abs(value - 1.0) <= tolerance for value in obj.scale)
        if not (location_ok and rotation_ok and scale_ok):
            issues.append({"name": obj.name, "location": list(obj.location), "rotation_euler": list(obj.rotation_euler), "scale": list(obj.scale)})
    return issues


def build_report(expected_version: str | None = None, expected_fps: int = 30) -> dict:
    state_before = snapshot()
    objects = sorted(bpy.data.objects, key=lambda item: item.name)
    meshes = [mesh_row(obj) for obj in objects if obj.type == "MESH"]
    armatures = [armature_row(obj) for obj in objects if obj.type == "ARMATURE"]
    associated_meshes = [row["name"] for row in meshes if row["armature_targets"] or (row["parent"] and row["parent"] in {armature["name"] for armature in armatures})]
    checks = [
        check("blend_loaded", "PASS" if bpy.data.filepath else "FAIL", "A .blend working copy is loaded." if bpy.data.filepath else "No .blend file is loaded.", True),
        check("armature_present", "PASS" if armatures else "FAIL", "%d armature object(s) found." % len(armatures), True),
        check("mesh_present", "PASS" if meshes else "FAIL", "%d mesh object(s) found." % len(meshes), True),
        check("mesh_armature_association", "PASS" if associated_meshes else "FAIL", "%d mesh object(s) are parented to or modified by an armature." % len(associated_meshes), True, associated_meshes),
    ]
    if expected_version:
        matches = bpy.app.version_string.startswith(expected_version)
        checks.append(check("blender_baseline", "PASS" if matches else "FAIL", "Loaded with expected Blender %s." % expected_version if matches else "Loaded read-only with Blender %s; expected %s." % (bpy.app.version_string, expected_version), False))

    finger_candidates = {
        armature["name"]: armature["semantic_candidates"] for armature in armatures
    }
    all_digits_mapped = bool(armatures) and all(
        candidates[digit][side]
        for candidates in finger_candidates.values()
        for digit in ("thumb", "index", "middle", "ring", "little")
        for side in ("left", "right")
    )
    checks.append(
        check(
            "semantic_finger_mapping",
            "PASS" if all_digits_mapped else "NOT YET TESTED",
            "All five digits on both sides have name-based candidates." if all_digits_mapped else "Bone inventory exists, but names alone do not prove every digit mapping; visual pose selection is still required.",
            False,
            finger_candidates,
        )
    )
    numbered_complete = bool(armatures)
    numbered_details = {}
    for armature in armatures:
        complete, details = has_numbered_finger_chains(armature)
        numbered_details[armature["name"]] = details
        numbered_complete = numbered_complete and complete
    checks.append(
        check(
            "numbered_finger_chain_structure",
            "PASS" if numbered_complete else "FAIL",
            "Five distinct, linked, rotation-available three-bone finger chains exist on each hand." if numbered_complete else "One or more expected numbered finger chains are missing, disconnected or fully rotation-locked.",
            True,
            numbered_details,
        )
    )
    wrist_mapped = any(
        mapping["wrist"][side]
        for mapping in finger_candidates.values()
        for side in ("left", "right")
    )
    checks.append(
        check(
            "wrist_control_structure",
            "PASS" if wrist_mapped else "NOT YET TESTED",
            "Wrist/hand pose-bone candidates exist; manipulation remains for TASK-0003." if wrist_mapped else "No unambiguous wrist/hand name candidate; visual selection is required.",
            False,
        )
    )
    total_constraints = sum(len(armature["constraints"]) for armature in armatures)
    checks.append(check("constraint_inventory", "PASS", "%d pose-bone constraints found; none were added or changed." % total_constraints, False))
    fps_matches = bpy.context.scene.render.fps == expected_fps
    checks.append(
        check(
            "fps_contract",
            "PASS" if fps_matches else "FAIL",
            "Scene FPS matches %d." % expected_fps if fps_matches else "Scene FPS is %d; project contract requires %d before animation/export." % (bpy.context.scene.render.fps, expected_fps),
            False,
        )
    )
    transform_issues = identity_transform_issues(objects)
    checks.append(
        check(
            "armature_object_transforms",
            "PASS" if not transform_issues else "FAIL",
            "Armature object transforms are identity." if not transform_issues else "%d armature object(s) have non-identity transforms; do not apply/fix them in this diagnostic task." % len(transform_issues),
            False,
            transform_issues,
        )
    )

    state_after = snapshot()
    checks.append(check("read_only_state", "PASS" if state_before == state_after else "FAIL", "Object/action/bone inventory is unchanged by inspection." if state_before == state_after else "Inspection changed Blender data state.", True))

    report = {
        "schema_version": 1,
        "inspection": "rig_inventory",
        "read_only": True,
        "overall_status": "FAIL" if any(row["status"] == "FAIL" for row in checks) else "PASS",
        "source": {
            "file": bpy.data.filepath,
            "basename": Path(bpy.data.filepath).name if bpy.data.filepath else None,
            "sha256": sha256(bpy.data.filepath),
            "blender_version": bpy.app.version_string,
        },
        "scene": {
            "active_scene": bpy.context.scene.name,
            "scenes": sorted(scene.name for scene in bpy.data.scenes),
            "collections": [
                {"name": collection.name, "objects": sorted(obj.name for obj in collection.objects), "children": sorted(child.name for child in collection.children)}
                for collection in sorted(bpy.data.collections, key=lambda item: item.name)
            ],
            "frame_start": bpy.context.scene.frame_start,
            "frame_end": bpy.context.scene.frame_end,
            "fps": bpy.context.scene.render.fps,
            "unit_system": bpy.context.scene.unit_settings.system,
            "selection": selection_state(),
        },
        "objects": [object_row(obj) for obj in objects],
        "meshes": meshes,
        "armatures": armatures,
        "actions": sorted(action.name for action in bpy.data.actions),
        "checks": checks,
    }
    return report


def emit_report(report: dict, output_path: str | None) -> None:
    print("Rig inventory: %d objects, %d meshes, %d armatures" % (len(report["objects"]), len(report["meshes"]), len(report["armatures"])))
    for armature in report["armatures"]:
        print("Armature %s: %d bones, %d deform, %d control candidates, %d constraints" % (armature["name"], armature["bone_count"], len(armature["deform_bones"]), len(armature["control_bones"]), len(armature["constraints"])))
    for row in report["checks"]:
        print("[%s] %s: %s" % (row["status"], row["id"], row["summary"]))
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    if output_path:
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialized + "\n", encoding="utf-8")
        print("JSON report: %s" % target)
    print("HCI_RIG_JSON_BEGIN")
    print(serialized)
    print("HCI_RIG_JSON_END")


def main() -> None:
    args = script_arguments()
    report = build_report(args.expected_version, args.expected_fps)
    emit_report(report, args.output)
    critical_failures = [row["id"] for row in report["checks"] if row["critical"] and row["status"] == "FAIL"]
    if critical_failures:
        raise RuntimeError("Critical rig preflight failures: %s" % ", ".join(critical_failures))


if __name__ == "__main__":
    main()
