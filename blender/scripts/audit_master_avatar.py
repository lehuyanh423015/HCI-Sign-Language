"""Read-only canonical master, facial capability and articulation audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import deque
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import establish_neutral_pose, evaluated_mesh_vertices, mesh_delta, sha256


FACIAL_NAME_RE = re.compile(
    r"head|neck|jaw|eye|oculi|orbicular|oris|temporalis|risorius|levator|depressor|mentalis|zygom|frontal|brow|special0[1-5]",
    re.IGNORECASE,
)
FACIAL_SHAPE_RE = re.compile(r"brow|blink|eye|mouth|lip|jaw|cheek|smile|frown|phoneme|viseme", re.IGNORECASE)
EXPECTED_MESHES = {"Human", "EDU_NeutralTop", "EDU_NeutralShorts"}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--baseline", default="docs/reports/artifacts/TASK-0002-rig-inventory.json")
    parser.add_argument("--expected-version", default="5.2.4")
    parser.add_argument("--expected-hash")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def hierarchy_rows(armature):
    return sorted(
        (bone.name, bone.parent.name if bone.parent else None, bool(bone.use_deform))
        for bone in armature.data.bones
    )


def hierarchy_sha256(rows):
    payload = "\n".join("%s|%s|%d" % (name, parent or "", int(deform)) for name, parent, deform in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def group_counts(mesh):
    by_index = {group.index: group.name for group in mesh.vertex_groups}
    counts = {group.name: 0 for group in mesh.vertex_groups}
    weights = {group.name: 0.0 for group in mesh.vertex_groups}
    for vertex in mesh.data.vertices:
        for membership in vertex.groups:
            name = by_index.get(membership.group)
            if name:
                counts[name] += 1
                weights[name] += membership.weight
    return {
        name: {"vertices": counts[name], "weight_sum": round(weights[name], 6)}
        for name in sorted(counts)
    }


def shape_key_inventory(mesh):
    shape_keys = mesh.data.shape_keys
    if not shape_keys:
        return []
    rows = []
    for key in shape_keys.key_blocks:
        relative = key.relative_key or shape_keys.reference_key
        distances = [(left.co - right.co).length for left, right in zip(key.data, relative.data)]
        moved = [distance for distance in distances if distance > 1e-7]
        facial_name = bool(FACIAL_SHAPE_RE.search(key.name))
        rows.append(
            {
                "object": mesh.name,
                "name": key.name,
                "value": key.value,
                "slider_min": key.slider_min,
                "slider_max": key.slider_max,
                "relative_key": relative.name,
                "moved_vertices": len(moved),
                "max_delta_m": max(distances, default=0.0),
                "mean_moved_delta_m": sum(moved) / len(moved) if moved else 0.0,
                "visible_geometry_delta": bool(moved),
                "facial_name_evidence": facial_name,
                "facial_animation_suitability": "NOT YET TESTED" if facial_name and moved else "NO",
                "reason": (
                    "Name suggests a facial target, but visual expression quality requires manual review."
                    if facial_name and moved
                    else "Basis key." if key == shape_keys.reference_key
                    else "No facial semantic in the actual key name; do not treat it as an expression."
                ),
            }
        )
    return rows


def connected_components(mesh):
    neighbors = [[] for _ in mesh.data.vertices]
    for edge in mesh.data.edges:
        left, right = edge.vertices
        neighbors[left].append(right)
        neighbors[right].append(left)
    visited = set()
    sizes = []
    for start in range(len(neighbors)):
        if start in visited:
            continue
        queue = deque([start])
        visited.add(start)
        size = 0
        while queue:
            current = queue.popleft()
            size += 1
            for neighbor in neighbors[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def pose_test(armature, mesh, bone_name, axis_index, degrees, head_threshold):
    establish_neutral_pose(armature)
    before = evaluated_mesh_vertices(mesh)
    before_object = tuple(round(value, 10) for row in armature.matrix_world for value in row)
    pose_bone = armature.pose.bones.get(bone_name)
    if pose_bone is None:
        return {"bone": bone_name, "status": "FAIL", "reason": "Bone missing"}
    original_mode = pose_bone.rotation_mode
    pose_bone.rotation_mode = "XYZ"
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)
    pose_bone.rotation_euler[axis_index] = math.radians(degrees)
    bpy.context.view_layer.update()
    after = evaluated_mesh_vertices(mesh)
    delta = mesh_delta(before, after)
    distances = [(right - left).length for left, right in zip(before, after)]
    below = [distance for point, distance in zip(before, distances) if point.z < head_threshold and distance > 1e-6]
    authored = [
        bone.name for bone in armature.pose.bones
        if not bone.matrix_basis.is_identity
    ]
    during_object = tuple(round(value, 10) for row in armature.matrix_world for value in row)
    pose_bone.rotation_mode = original_mode
    pose_bone.matrix_basis.identity()
    bpy.context.view_layer.update()
    reset = evaluated_mesh_vertices(mesh)
    reset_delta = mesh_delta(before, reset)
    passed = (
        delta["moved_vertices"] > 0
        and authored == [bone_name]
        and before_object == during_object
        and reset_delta["max_distance"] <= 1e-6
    )
    return {
        "bone": bone_name,
        "parent": pose_bone.parent.name if pose_bone.parent else None,
        "axis": "XYZ"[axis_index],
        "degrees": degrees,
        "status": "PASS" if passed else "FAIL",
        "authored_pose_changes": authored,
        "mesh_delta": delta,
        "moved_vertices_below_head_threshold": len(below),
        "max_delta_below_head_threshold_m": max(below, default=0.0),
        "object_transform_stable": before_object == during_object,
        "reset_mesh_delta": reset_delta,
    }


def feature_support(feature, evidence, method, priority):
    return {
        "feature": feature,
        "existing_support": evidence,
        "recommended_method": method,
        "priority": priority,
    }


def main():
    args = arguments()
    output = Path(args.output).resolve()
    source_hash = sha256(bpy.data.filepath)
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or armature.type != "ARMATURE" or body is None or body.type != "MESH":
        raise RuntimeError("Human/Human.rig canonical objects are missing")

    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    baseline_rows = sorted(
        (bone["name"], bone["parent"], bool(bone["use_deform"]))
        for bone in baseline["armatures"][0]["bones"]
    )
    current_rows = hierarchy_rows(armature)
    groups = group_counts(body)
    bones = {bone.name: bone for bone in armature.data.bones}
    facial_bones = []
    for name, bone in sorted(bones.items()):
        if FACIAL_NAME_RE.search(name):
            weight = groups.get(name, {"vertices": 0, "weight_sum": 0.0})
            facial_bones.append(
                {
                    "name": name,
                    "parent": bone.parent.name if bone.parent else None,
                    "use_deform": bone.use_deform,
                    "weighted_vertices": weight["vertices"],
                    "weight_sum": weight["weight_sum"],
                }
            )

    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    associations = []
    for mesh in sorted(meshes, key=lambda item: item.name):
        targets = sorted(
            modifier.object.name for modifier in mesh.modifiers
            if modifier.type == "ARMATURE" and modifier.object
        )
        associations.append(
            {
                "mesh": mesh.name,
                "parent": mesh.parent.name if mesh.parent else None,
                "armature_modifier_targets": targets,
                "vertex_groups": len(mesh.vertex_groups),
                "all_vertices_weighted": all(bool(vertex.groups) for vertex in mesh.data.vertices),
            }
        )

    shape_keys = [row for mesh in meshes for row in shape_key_inventory(mesh)]
    facial_shape_keys = [row for row in shape_keys if row["facial_name_evidence"]]
    component_sizes = connected_components(body)
    neck_top = armature.matrix_world @ armature.data.bones["neck03"].tail_local
    head_vertices = [
        body.matrix_world @ vertex.co for vertex in body.data.vertices
        if (body.matrix_world @ vertex.co).z >= neck_top.z
    ]
    facial_weight_groups = {
        name: row for name, row in groups.items()
        if FACIAL_NAME_RE.search(name) and row["vertices"] > 0
    }
    topology = {
        "body_object": body.name,
        "body_vertex_count_raw": len(body.data.vertices),
        "body_edge_count_raw": len(body.data.edges),
        "body_polygon_count_raw": len(body.data.polygons),
        "connected_component_count_raw": len(component_sizes),
        "largest_connected_components": component_sizes[:12],
        "head_region_threshold_world_z": neck_top.z,
        "head_region_vertex_count_raw": len(head_vertices),
        "mesh_objects": sorted(mesh.name for mesh in meshes),
        "separate_eye_mesh_objects": sorted(mesh.name for mesh in meshes if re.search(r"eye", mesh.name, re.I)),
        "separate_eyebrow_mesh_objects": sorted(mesh.name for mesh in meshes if re.search(r"brow", mesh.name, re.I)),
        "body_materials": [slot.material.name if slot.material else None for slot in body.material_slots],
        "facial_weight_groups": facial_weight_groups,
        "evidence_interpretation": (
            "Eyes/eyebrows are not separate Blender objects. Facial deformation must use weighted integrated geometry; "
            "raw connected components and bone weights do not by themselves prove production-quality eyelid/lip loops."
        ),
    }

    head_threshold = neck_top.z - 0.02
    articulation = [
        pose_test(armature, body, "head", 2, 6.0, head_threshold),
        pose_test(armature, body, "neck02", 2, 6.0, head_threshold),
        pose_test(armature, body, "jaw", 0, 6.0, head_threshold),
        pose_test(armature, body, "eye.L", 2, 6.0, head_threshold),
        pose_test(armature, body, "eye.R", 2, 6.0, head_threshold),
    ]
    establish_neutral_pose(armature)

    def weighted(*names):
        return all(name in groups and groups[name]["vertices"] > 0 for name in names)

    matrix = [
        feature_support("Eyebrow raise", "No explicit brow Shape Key/control; nearby facial deform bones exist but expression quality is NOT YET TESTED.", "Shape Keys", "High"),
        feature_support("Eye blink", "No blink Shape Key; oculi/orbicularis weighted bones exist, but a blink has not been authored or visually approved.", "Shape Keys", "High"),
        feature_support("Eye direction", "eye.L/eye.R exist with weights and controlled deformation test: %s." % ("PASS" if weighted("eye.L", "eye.R") and all(row["status"] == "PASS" for row in articulation[3:]) else "FAIL"), "Eye bones", "High"),
        feature_support("Mouth open", "jaw exists with weights and controlled deformation test: %s; articulation quality is NOT YET TESTED." % articulation[2]["status"], "Jaw bone + corrective Shape Keys", "High"),
        feature_support("Lip shape", "Multiple oris deform bones have weights; no phoneme/viseme Shape Keys and no production lip poses.", "Shape Keys", "High"),
        feature_support("Cheek movement", "risorius/levator/temporalis groups exist; no approved cheek expressions.", "Shape Keys + existing deform bones", "Medium"),
        feature_support("Head rotation", "head controlled deformation test: %s." % articulation[0]["status"], "Existing head bone", "High"),
        feature_support("Neck movement", "neck01/02/03 hierarchy exists; neck02 controlled deformation test: %s." % articulation[1]["status"], "Existing neck bones", "High"),
        feature_support("Upper-body posture", "Existing spine/clavicle/arm deformation rig and prior controlled hand/arm tests are available.", "Existing rig", "Medium"),
    ]

    armature_rotation = list(armature.rotation_euler)
    expected_rotation = [-0.055045463144779205, 0.002965844003483653, -0.244863823056221]
    rotation_retained = all(abs(left - right) <= 1e-7 for left, right in zip(armature_rotation, expected_rotation))
    actions = sorted(action.name for action in bpy.data.actions)
    checks = [
        {"id": "blender_version", "status": "PASS" if bpy.app.version_string.startswith(args.expected_version) else "FAIL"},
        {"id": "canonical_hash", "status": "PASS" if not args.expected_hash or source_hash.upper() == args.expected_hash.upper() else "FAIL"},
        {"id": "bone_count", "status": "PASS" if len(current_rows) == 137 else "FAIL", "actual": len(current_rows)},
        {"id": "baseline_hierarchy", "status": "PASS" if current_rows == baseline_rows else "FAIL"},
        {"id": "expected_meshes", "status": "PASS" if EXPECTED_MESHES.issubset({mesh.name for mesh in meshes}) else "FAIL"},
        {"id": "mesh_armature_association", "status": "PASS" if all("Human.rig" in row["armature_modifier_targets"] for row in associations) else "FAIL"},
        {"id": "finger_chains", "status": "PASS" if all("finger%d-%d.%s" % (digit, joint, side) in bones for side in ("L", "R") for digit in range(1, 6) for joint in range(1, 4)) else "FAIL"},
        {"id": "canonical_no_actions", "status": "PASS" if not actions else "FAIL", "actions": actions},
        {"id": "neutral_pose", "status": "PASS" if all(bone.matrix_basis.is_identity for bone in armature.pose.bones) else "FAIL"},
        {"id": "fps", "status": "PASS" if bpy.context.scene.render.fps == 30 else "FAIL", "actual": bpy.context.scene.render.fps},
        {"id": "armature_rotation_retained", "status": "PASS" if rotation_retained else "FAIL", "actual": armature_rotation},
        {"id": "head_neck_deformation", "status": "PASS" if all(row["status"] == "PASS" for row in articulation[:2]) else "FAIL"},
        {"id": "shape_key_inventory", "status": "PASS", "count": len(shape_keys)},
        {"id": "facial_shape_keys", "status": "NOT YET TESTED" if not facial_shape_keys else "PASS", "count": len(facial_shape_keys)},
    ]
    report = {
        "schema_version": 1,
        "inspection": "canonical_master_and_facial_capability",
        "read_only": True,
        "overall_status": "FAIL" if any(row["status"] == "FAIL" for row in checks) else "PASS",
        "source": {
            "path": bpy.data.filepath,
            "sha256": source_hash,
            "blender_version": bpy.app.version_string,
            "master_version": bpy.context.scene.get("master_avatar_version"),
        },
        "scene": {
            "fps": bpy.context.scene.render.fps,
            "frame_range": [bpy.context.scene.frame_start, bpy.context.scene.frame_end],
            "actions": actions,
        },
        "rig": {
            "armature": armature.name,
            "bone_count": len(current_rows),
            "deform_bone_count": sum(1 for _, _, deform in current_rows if deform),
            "hierarchy_sha256": hierarchy_sha256(current_rows),
            "matches_task0002_baseline": current_rows == baseline_rows,
            "object_rotation_euler": armature_rotation,
            "non_identity_rotation_policy": "Retained; TASK-0003/0004 GLB pipeline is compatible. Do not apply blindly.",
            "facial_bones": facial_bones,
        },
        "mesh_armature_associations": associations,
        "shape_keys": shape_keys,
        "facial_topology": topology,
        "controlled_articulation": articulation,
        "facial_capability_matrix": matrix,
        "checks": checks,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in checks:
        print("[%s] %s" % (row["status"], row["id"]))
    print("Facial bones: %d; shape keys: %d; facial-named shape keys: %d" % (len(facial_bones), len(shape_keys), len(facial_shape_keys)))
    print("JSON report: %s" % output)
    if report["overall_status"] == "FAIL":
        raise RuntimeError("Canonical master audit failed")


if __name__ == "__main__":
    main()
