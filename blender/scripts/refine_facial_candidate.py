"""Create the TASK-0007A refined facial candidate from TASK-0006 source."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_facial_geometry import BROW_TARGETS, EYE_OBJECTS, brow_record, eye_basis, projected_bounds, socket_proxy
from rig_control_utils import matrix_signature, sha256


SOURCE_SHA256 = "4F4BA651A8E15B356FBA18625826E5A0EBF29CBF631746A6B295DA667B27A982"
CANONICAL_SHA256 = "A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232"
CANDIDATE_VERSION = "1.0.0-rc.3"
HIERARCHY_SHA256 = "6A8C8B4B2C2E71446A79E478E15F3FFE1A646F24EFF86C3C9C158315AAFE72C2"
TARGETS = (
    "NMM_BROW_RAISE_L", "NMM_BROW_RAISE_R", "NMM_EYE_BLINK_L",
    "NMM_EYE_BLINK_R", "NMM_LIPS_ROUND", "NMM_LIPS_SPREAD",
)
ACTIONS = ("NMM_BLINK_TEST", "NMM_BROW_TEST", "NMM_MOUTH_TEST", "TECH_HAND_FACE_TEST")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def hierarchy_signature(armature):
    rows = sorted(
        "%s|%s|%d" % (bone.name, bone.parent.name if bone.parent else "", int(bone.use_deform))
        for bone in armature.data.bones
    )
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest().upper()


def coordinate_hash(key):
    digest = hashlib.sha256()
    for point in key.data:
        digest.update(("%.9f,%.9f,%.9f;" % tuple(point.co)).encode("ascii"))
    return digest.hexdigest().upper()


def object_center(obj):
    basis = obj.data.shape_keys.reference_key if obj.data.shape_keys else None
    points = basis.data if basis else obj.data.vertices
    return sum((point.co for point in points), Vector()) / len(points)


def eye_measurement(body, armature, side):
    basis = eye_basis(armature, side)
    names = EYE_OBJECTS[side]
    eyeball = projected_bounds(bpy.data.objects[names[0]], basis)
    iris = projected_bounds(bpy.data.objects[names[1]], basis)
    pupil = projected_bounds(bpy.data.objects[names[2]], basis)
    center = Vector(eyeball["center_local_m"])
    socket = socket_proxy(body, center, basis)
    return {
        "eyeball": eyeball,
        "iris": iris,
        "pupil": pupil,
        "socket_proxy": socket,
        "protrusion_vs_socket_median_m": round(
            eyeball["extents_m"]["forward"][1] - socket["forward_surface_m"]["median"], 9
        ),
    }


def transform_eye_assembly(body, armature, side):
    lateral, forward, up = eye_basis(armature, side)
    names = EYE_OBJECTS[side]
    objects = [bpy.data.objects[name] for name in names]
    old_centers = {obj.name: object_center(obj) for obj in objects}
    old_eye_center = old_centers[names[0]]

    old_radius = projected_bounds(objects[0], (lateral, forward, up))["dimensions_m"]["lateral"] * 0.5
    scale = 0.78
    new_radius = old_radius * scale
    recess_m = 0.0035
    new_eye_center = old_eye_center - forward * recess_m
    new_centers = {
        names[0]: new_eye_center,
        names[1]: new_eye_center + forward * (new_radius * 0.91),
        names[2]: new_eye_center + forward * (new_radius * 1.015),
    }
    axis_scales = {
        names[0]: (scale, scale, scale),
        names[1]: (0.76, 0.75, 0.76),
        names[2]: (0.75, 0.75, 0.75),
    }

    rows = []
    for obj in objects:
        if not obj.data.shape_keys or len(obj.data.shape_keys.key_blocks) < 2:
            raise RuntimeError("Eye object missing blink Shape Key: %s" % obj.name)
        blink_name = "NMM_EYE_BLINK_%s" % side
        keys = obj.data.shape_keys.key_blocks
        basis_key = obj.data.shape_keys.reference_key
        if keys.get(blink_name) is None:
            raise RuntimeError("Missing %s on %s" % (blink_name, obj.name))
        old_center = old_centers[obj.name]
        new_center = new_centers[obj.name]
        sx, sf, su = axis_scales[obj.name]
        for point in basis_key.data:
            relative = point.co - old_center
            point.co = (
                new_center
                + lateral * (lateral.dot(relative) * sx)
                + forward * (forward.dot(relative) * sf)
                + up * (up.dot(relative) * su)
            )
        blink = keys[blink_name]
        for index, point in enumerate(basis_key.data):
            relative = point.co - new_center
            blink.data[index].co = (
                new_center
                + lateral * lateral.dot(relative)
                + forward * (forward.dot(relative) - 0.016)
                + up * (up.dot(relative) * 0.05)
            )
        obj["task0007a_refinement"] = "measured_scale_and_recess"
        obj["task0007a_scale_factor"] = scale if obj.name == names[0] else axis_scales[obj.name][0]
        obj["task0007a_recess_m"] = recess_m
        rows.append({
            "object": obj.name,
            "old_center_local_m": [round(value, 9) for value in old_center],
            "new_center_local_m": [round(value, 9) for value in new_center],
            "axis_scale": list(axis_scales[obj.name]),
            "blink_target": blink_name,
        })
    return rows


def refine_brows(body):
    keys = body.data.shape_keys.key_blocks
    basis = body.data.shape_keys.reference_key
    before = {name: brow_record(body, name) for name in BROW_TARGETS}
    vertical_scale = 2.0
    vertical_smooth_add_m = 0.002
    forward_scale = 1.35
    rows = []
    for name in BROW_TARGETS:
        key = keys[name]
        original_deltas = [target.co - source.co for target, source in zip(key.data, basis.data)]
        max_up = max(delta.z for delta in original_deltas)
        for index, source in enumerate(basis.data):
            delta = original_deltas[index]
            if delta.length <= 1e-7:
                continue
            normalized_up = max(delta.z, 0.0) / max_up if max_up > 0.0 else 0.0
            smooth_add = vertical_smooth_add_m * math.sqrt(normalized_up)
            key.data[index].co = source.co + Vector((
                delta.x,
                delta.y * forward_scale,
                delta.z * vertical_scale + smooth_add,
            ))
        rows.append({
            "name": name,
            "method": "amplify existing localized deformation with smooth strength-weighted lift; no new affected vertices",
            "vertical_scale": vertical_scale,
            "vertical_smooth_add_m": vertical_smooth_add_m,
            "forward_scale": forward_scale,
            "before": before[name],
            "after": brow_record(body, name),
        })
    return rows


def main():
    args = arguments()
    source = Path(bpy.data.filepath).resolve()
    output = Path(args.output_blend).resolve()
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    if sha256(source) != SOURCE_SHA256:
        raise RuntimeError("TASK-0006 candidate hash mismatch")
    if source == output:
        raise RuntimeError("Refusing to overwrite TASK-0006 source candidate")

    body = bpy.data.objects.get("Human")
    armature = bpy.data.objects.get("Human.rig")
    if not body or not armature or not body.data.shape_keys:
        raise RuntimeError("Human/Human.rig/Shape Keys missing")
    if len(armature.data.bones) != 137 or hierarchy_signature(armature) != HIERARCHY_SHA256:
        raise RuntimeError("Armature hierarchy mismatch")
    if any(bpy.data.objects.get(name) is None for names in EYE_OBJECTS.values() for name in names):
        raise RuntimeError("Eye geometry inventory incomplete")
    if any(body.data.shape_keys.key_blocks.get(name) is None for name in TARGETS):
        raise RuntimeError("NMM target inventory incomplete")
    if any(bpy.data.actions.get(name) is None for name in ACTIONS):
        raise RuntimeError("Technical clip inventory incomplete")

    hierarchy_before = hierarchy_signature(armature)
    armature_matrix_before = matrix_signature(armature.matrix_world)
    key_hashes_before = {key.name: coordinate_hash(key) for key in body.data.shape_keys.key_blocks}
    neutral_body_hash = coordinate_hash(body.data.shape_keys.reference_key)
    eyes_before = {side: eye_measurement(body, armature, side) for side in ("L", "R")}

    eye_changes = {side: transform_eye_assembly(body, armature, side) for side in ("L", "R")}
    brow_changes = refine_brows(body)
    eyes_after = {side: eye_measurement(body, armature, side) for side in ("L", "R")}

    preserved_keys = {}
    for key in body.data.shape_keys.key_blocks:
        if key.name not in BROW_TARGETS:
            preserved_keys[key.name] = key_hashes_before[key.name] == coordinate_hash(key)
    if not all(preserved_keys.values()):
        raise RuntimeError("A non-brow body Shape Key changed")
    if neutral_body_hash != coordinate_hash(body.data.shape_keys.reference_key):
        raise RuntimeError("Neutral body geometry changed")
    if hierarchy_before != hierarchy_signature(armature) or armature_matrix_before != matrix_signature(armature.matrix_world):
        raise RuntimeError("Armature structure or transform changed")

    scene = bpy.context.scene
    scene["master_avatar_version"] = CANDIDATE_VERSION
    scene["master_avatar_status"] = "experimental-refined-owner-review-candidate"
    scene["master_avatar_source_candidate_sha256"] = SOURCE_SHA256
    scene["master_avatar_source_sha256"] = CANONICAL_SHA256
    scene["task0007a_eye_scale_factor"] = 0.78
    scene["task0007a_eye_recess_m"] = 0.0035
    scene["task0007a_brow_vertical_scale"] = 2.0
    scene["task0007a_brow_vertical_smooth_add_m"] = 0.002

    output.parent.mkdir(parents=True, exist_ok=True)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    output_hash = sha256(output)

    manifest = {
        "schema_version": 1,
        "candidate_name": "Master Avatar v1.0.0-rc.3",
        "candidate_version": CANDIDATE_VERSION,
        "status": "experimental-owner-review-candidate",
        "blender_version": bpy.app.version_string,
        "mpfb_version": "2.0.18",
        "source_candidate_path": "blender/working/huy-anh/task-0006-facial-foundation/avatar_master_facial_candidate.blend",
        "source_candidate_sha256": SOURCE_SHA256,
        "refined_candidate_path": "blender/working/huy-anh/task-0007a-facial-refinement/avatar_master_facial_refined_candidate.blend",
        "refined_candidate_sha256": output_hash,
        "bone_count": len(armature.data.bones),
        "hierarchy_sha256": hierarchy_signature(armature),
        "mesh_count": sum(obj.type == "MESH" for obj in scene.objects),
        "eye_geometry_measurements": {"before": eyes_before, "after": eyes_after},
        "morph_target_names": list(TARGETS),
        "animation_clip_names": list(ACTIONS),
        "export_glb_path": "assets/exports/technical/task-0007a/technical-facial-refined-test.glb",
        "validation_status": "NOT YET TESTED",
        "owner_acceptance": "NOT YET TESTED",
        "linguistic_validity": "NOT YET TESTED",
    }
    manifest_path = Path(args.manifest).resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema_version": 1,
        "artifact": "task0007a_refined_candidate_creation",
        "status": "PASS",
        "technical_fixture_only": True,
        "source": {"path": str(source), "sha256": SOURCE_SHA256},
        "output": {"path": str(output), "sha256": output_hash},
        "preservation": {
            "separate_output": source != output,
            "bone_count": len(armature.data.bones),
            "hierarchy_unchanged": hierarchy_before == hierarchy_signature(armature),
            "armature_transform_unchanged": armature_matrix_before == matrix_signature(armature.matrix_world),
            "neutral_body_geometry_unchanged": neutral_body_hash == coordinate_hash(body.data.shape_keys.reference_key),
            "non_brow_body_shape_keys_unchanged": all(preserved_keys.values()),
        },
        "eye_measurements_before": eyes_before,
        "eye_changes": eye_changes,
        "eye_measurements_after": eyes_after,
        "brow_changes": brow_changes,
        "morph_targets": list(TARGETS),
        "actions": list(ACTIONS),
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS refined facial candidate: %s" % output)
    print("SHA-256: %s" % output_hash)


if __name__ == "__main__":
    main()
