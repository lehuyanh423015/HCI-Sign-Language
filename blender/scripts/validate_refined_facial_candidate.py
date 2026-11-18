"""Validate TASK-0007A refined candidate without modifying the blend file."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_facial_geometry import BROW_TARGETS, EYE_OBJECTS, brow_record, eye_basis, projected_bounds, socket_proxy
from rig_control_utils import action_fcurves, matrix_signature, sha256


CANONICAL_SHA256 = "A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232"
SOURCE_SHA256 = "4F4BA651A8E15B356FBA18625826E5A0EBF29CBF631746A6B295DA667B27A982"
HIERARCHY_SHA256 = "6A8C8B4B2C2E71446A79E478E15F3FFE1A646F24EFF86C3C9C158315AAFE72C2"
TARGETS = {
    "NMM_BROW_RAISE_L", "NMM_BROW_RAISE_R", "NMM_EYE_BLINK_L",
    "NMM_EYE_BLINK_R", "NMM_LIPS_ROUND", "NMM_LIPS_SPREAD",
}
ACTIONS = {"NMM_BLINK_TEST", "NMM_BROW_TEST", "NMM_MOUTH_TEST", "TECH_HAND_FACE_TEST"}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--artifact-manifest", required=True)
    parser.add_argument("--glb-validation-report")
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def hierarchy_signature(armature):
    rows = sorted(
        "%s|%s|%d" % (bone.name, bone.parent.name if bone.parent else "", int(bone.use_deform))
        for bone in armature.data.bones
    )
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest().upper()


def check(identifier, passed, actual):
    return {"id": identifier, "status": "PASS" if passed else "FAIL", "actual": actual}


def eye_record(body, armature, side):
    lateral, forward, up = eye_basis(armature, side)
    names = EYE_OBJECTS[side]
    objects = [bpy.data.objects.get(name) for name in names]
    if any(obj is None for obj in objects):
        return {"side": side, "missing": names}
    eyeball = projected_bounds(objects[0], (lateral, forward, up))
    center = eyeball["center_local_m"]
    socket = socket_proxy(body, __import__("mathutils").Vector(center), (lateral, forward, up))
    bindings = []
    for obj in objects:
        bone_name = "eye.%s" % side
        group = obj.vertex_groups.get(bone_name)
        weighted = 0
        if group:
            weighted = sum(
                any(item.group == group.index and abs(item.weight - 1.0) < 1e-6 for item in vertex.groups)
                for vertex in obj.data.vertices
            )
        bindings.append({
            "object": obj.name, "vertices": len(obj.data.vertices), "fully_weighted": weighted,
            "armature_modifiers": [mod.object.name for mod in obj.modifiers if mod.type == "ARMATURE" and mod.object],
            "blink_target": "NMM_EYE_BLINK_%s" % side,
            "blink_target_present": bool(obj.data.shape_keys and obj.data.shape_keys.key_blocks.get("NMM_EYE_BLINK_%s" % side)),
        })
    return {
        "side": side,
        "eyeball": eyeball,
        "iris": projected_bounds(objects[1], (lateral, forward, up)),
        "pupil": projected_bounds(objects[2], (lateral, forward, up)),
        "socket_proxy": socket,
        "protrusion_vs_socket_median_m": round(
            eyeball["extents_m"]["forward"][1] - socket["forward_surface_m"]["median"], 9
        ),
        "bindings": bindings,
    }


def main():
    args = arguments()
    body = bpy.data.objects.get("Human")
    armature = bpy.data.objects.get("Human.rig")
    if not body or not armature or not body.data.shape_keys:
        raise RuntimeError("Human/Human.rig/Shape Keys missing")
    keys = body.data.shape_keys.key_blocks
    eyes = {side: eye_record(body, armature, side) for side in ("L", "R")}
    brows = [brow_record(body, name) for name in BROW_TARGETS]

    checks = [
        check("blender_version", bpy.app.version_string.startswith(args.expected_version), bpy.app.version_string),
        check("candidate_is_separate", Path(bpy.data.filepath).name == "avatar_master_facial_refined_candidate.blend", bpy.data.filepath),
        check("candidate_version", bpy.context.scene.get("master_avatar_version") == "1.0.0-rc.3", bpy.context.scene.get("master_avatar_version")),
        check("canonical_source_metadata", bpy.context.scene.get("master_avatar_source_sha256") == CANONICAL_SHA256, bpy.context.scene.get("master_avatar_source_sha256")),
        check("task0006_source_metadata", bpy.context.scene.get("master_avatar_source_candidate_sha256") == SOURCE_SHA256, bpy.context.scene.get("master_avatar_source_candidate_sha256")),
        check("bone_count", len(armature.data.bones) == 137, len(armature.data.bones)),
        check("hierarchy", hierarchy_signature(armature) == HIERARCHY_SHA256, hierarchy_signature(armature)),
        check("nmm_targets", TARGETS.issubset(keys.keys()), sorted(name for name in keys.keys() if name.startswith("NMM_"))),
    ]
    for side, row in eyes.items():
        diameter = row["eyeball"]["dimensions_m"]["lateral"]
        checks.append(check("eye_%s_diameter" % side, 0.0185 <= diameter <= 0.0200, diameter))
        checks.append(check("eye_%s_depth" % side, 0.0 <= row["protrusion_vs_socket_median_m"] <= 0.0060, row["protrusion_vs_socket_median_m"]))
        checks.append(check("eye_%s_binding" % side, all(
            item["fully_weighted"] == item["vertices"]
            and "Human.rig" in item["armature_modifiers"]
            and item["blink_target_present"]
            for item in row["bindings"]
        ), row["bindings"]))
    checks.append(check("eye_symmetry", abs(
        eyes["L"]["eyeball"]["dimensions_m"]["lateral"] - eyes["R"]["eyeball"]["dimensions_m"]["lateral"]
    ) < 1e-6 and abs(
        eyes["L"]["protrusion_vs_socket_median_m"] - eyes["R"]["protrusion_vs_socket_median_m"]
    ) < 1e-6, {"left": eyes["L"], "right": eyes["R"]}))

    basis = body.data.shape_keys.reference_key
    target_rows = []
    for name in sorted(TARGETS):
        key = keys.get(name)
        distances = [(a.co - b.co).length for a, b in zip(key.data, basis.data)] if key else []
        moved = [distance for distance in distances if distance > 1e-7]
        row = {
            "name": name, "moved_vertices": len(moved),
            "max_delta_m": max(moved) if moved else 0.0,
            "value": key.value if key else None,
        }
        target_rows.append(row)
        checks.append(check("target_%s" % name, bool(
            key and moved and key.slider_min == 0.0 and key.slider_max == 1.0 and key.value == 0.0
        ), row))
    for row in brows:
        checks.append(check("%s_interpolation_readability" % row["name"],
            row["interpolation"]["0.5_max_delta_m"] >= 0.0065
            and row["interpolation"]["1.0_max_delta_m"] >= 0.013,
            row["interpolation"],
        ))

    action_rows = []
    for name in sorted(ACTIONS):
        action = bpy.data.actions.get(name)
        slots = list(action.slots) if action else []
        curves = sum((list(action_fcurves(action, slot)) for slot in slots), []) if action else []
        row = {"name": name, "slot_types": sorted(slot.target_id_type for slot in slots), "fcurves": len(curves)}
        action_rows.append(row)
        checks.append(check("action_%s" % name, bool(action and {"OBJECT", "KEY"}.issubset(row["slot_types"]) and curves), row))
    combined = bpy.data.actions.get("TECH_HAND_FACE_TEST")
    paths = []
    if combined:
        for slot in combined.slots:
            paths.extend(curve.data_path for curve in action_fcurves(combined, slot))
    checks.append(check("combined_hand_face_channels",
        any("finger" in path and ".R" in path for path in paths)
        and any("head" in path for path in paths)
        and any("jaw" in path for path in paths)
        and any("NMM_" in path for path in paths), sorted(set(paths))))

    glb_status = "NOT YET TESTED"
    if args.glb_validation_report:
        glb_path = Path(args.glb_validation_report).resolve()
        if glb_path.exists():
            glb_status = json.loads(glb_path.read_text(encoding="utf-8"))["status"]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "schema_version": 1, "artifact": "task0007a_refined_candidate_validation",
        "source": {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)},
        "status": status, "glb_validation_status": glb_status,
        "armature_matrix": matrix_signature(armature.matrix_world),
        "eyes": eyes, "brows": brows, "morph_targets": target_rows,
        "actions": action_rows, "checks": checks,
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source_manifest_path = Path(args.source_manifest).resolve()
    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    manifest["refined_candidate_sha256"] = sha256(bpy.data.filepath)
    manifest["eye_geometry_measurements"]["validated_after"] = eyes
    manifest["brow_interpolation_measurements"] = brows
    manifest["candidate_validation_status"] = status
    manifest["glb_validation_status"] = glb_status
    manifest["validation_status"] = "PASS" if status == "PASS" and glb_status == "PASS" else ("FAIL" if "FAIL" in (status, glb_status) else "PARTIAL")
    source_manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifact_manifest = Path(args.artifact_manifest).resolve()
    artifact_manifest.parent.mkdir(parents=True, exist_ok=True)
    artifact_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for item in checks:
        print("%s refined candidate: %s" % (item["status"], item["id"]))
    print("%s refined candidate validation" % status)
    if status != "PASS":
        raise RuntimeError("Refined candidate validation failed")


if __name__ == "__main__":
    main()
