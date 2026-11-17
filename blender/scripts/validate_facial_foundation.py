"""Validate the TASK-0006 facial candidate without modifying it."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import action_fcurves, matrix_signature, sha256


CANONICAL_SHA256 = "A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232"
TARGETS = {
    "NMM_BROW_RAISE_L", "NMM_BROW_RAISE_R", "NMM_EYE_BLINK_L",
    "NMM_EYE_BLINK_R", "NMM_LIPS_ROUND", "NMM_LIPS_SPREAD",
}
ACTIONS = {"NMM_BLINK_TEST", "NMM_BROW_TEST", "NMM_MOUTH_TEST", "TECH_HAND_FACE_TEST"}
EYES = {
    "NMM_Eyeball.L": "eye.L", "NMM_Iris.L": "eye.L", "NMM_Pupil.L": "eye.L",
    "NMM_Eyeball.R": "eye.R", "NMM_Iris.R": "eye.R", "NMM_Pupil.R": "eye.R",
}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def hierarchy_signature(armature):
    rows = sorted("%s|%s|%d" % (bone.name, bone.parent.name if bone.parent else "", int(bone.use_deform)) for bone in armature.data.bones)
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest().upper()


def check(identifier, passed, actual):
    return {"id": identifier, "status": "PASS" if passed else "FAIL", "actual": actual}


def main():
    args = arguments()
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or body is None or body.data.shape_keys is None:
        raise RuntimeError("Human/Human.rig/Shape Keys missing")
    keys = body.data.shape_keys.key_blocks
    checks = [
        check("blender_version", bpy.app.version_string.startswith(args.expected_version), bpy.app.version_string),
        check("candidate_is_separate", Path(bpy.data.filepath).name == "avatar_master_facial_candidate.blend", bpy.data.filepath),
        check("canonical_source_metadata", bpy.context.scene.get("master_avatar_source_sha256") == CANONICAL_SHA256, bpy.context.scene.get("master_avatar_source_sha256")),
        check("candidate_version", bpy.context.scene.get("master_avatar_version") == "1.0.0-rc.2", bpy.context.scene.get("master_avatar_version")),
        check("bone_count", len(armature.data.bones) == 137, len(armature.data.bones)),
        check("hierarchy", hierarchy_signature(armature) == "6A8C8B4B2C2E71446A79E478E15F3FFE1A646F24EFF86C3C9C158315AAFE72C2", hierarchy_signature(armature)),
        check("nmm_targets", TARGETS.issubset(keys.keys()), sorted(name for name in keys.keys() if name.startswith("NMM_"))),
    ]
    target_rows = []
    basis = body.data.shape_keys.reference_key
    for name in sorted(TARGETS):
        key = keys.get(name)
        distances = [(a.co - b.co).length for a, b in zip(key.data, basis.data)] if key else []
        moved = [value for value in distances if value > 1e-7]
        row = {"name": name, "moved_vertices": len(moved), "max_delta_m": max(moved) if moved else 0.0, "value": key.value if key else None}
        target_rows.append(row)
        checks.append(check("target_%s" % name, bool(key and moved and key.slider_min == 0.0 and key.slider_max == 1.0 and key.value == 0.0), row))
    eye_rows = []
    for name, bone_name in EYES.items():
        obj = bpy.data.objects.get(name)
        group = obj.vertex_groups.get(bone_name) if obj else None
        weighted = 0
        if obj and group:
            weighted = sum(any(item.group == group.index and abs(item.weight - 1.0) < 1e-6 for item in vertex.groups) for vertex in obj.data.vertices)
        armature_modifiers = [mod.object.name for mod in obj.modifiers if mod.type == "ARMATURE" and mod.object] if obj else []
        row = {"name": name, "bone": bone_name, "vertices": len(obj.data.vertices) if obj else 0, "fully_weighted": weighted, "armature_modifiers": armature_modifiers}
        eye_rows.append(row)
        checks.append(check("eye_%s" % name, bool(obj and weighted == len(obj.data.vertices) and armature.name in armature_modifiers), row))
    action_rows = []
    for name in sorted(ACTIONS):
        action = bpy.data.actions.get(name)
        slots = list(action.slots) if action else []
        curves = sum((list(action_fcurves(action, slot)) for slot in slots), []) if action else []
        row = {"name": name, "slot_types": sorted(slot.target_id_type for slot in slots), "fcurves": len(curves), "keyframe_points": sum(len(curve.keyframe_points) for curve in curves)}
        action_rows.append(row)
        checks.append(check("action_%s" % name, bool(action and {"OBJECT", "KEY"}.issubset(row["slot_types"]) and row["fcurves"] > 0), row))
    combined = bpy.data.actions.get("TECH_HAND_FACE_TEST")
    combined_paths = []
    if combined:
        for slot in combined.slots:
            combined_paths.extend(curve.data_path for curve in action_fcurves(combined, slot))
    checks.append(check("combined_hand_face_channels", any("finger" in path and ".R" in path for path in combined_paths) and any("head" in path for path in combined_paths) and any("jaw" in path for path in combined_paths) and any("NMM_" in path for path in combined_paths), sorted(set(combined_paths))))
    report = {
        "schema_version": 1, "artifact": "task0006_facial_candidate_validation",
        "source": {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)},
        "armature_matrix": matrix_signature(armature.matrix_world),
        "morph_targets": target_rows, "eye_assets": eye_rows, "actions": action_rows,
        "checks": checks, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in checks:
        print("%s candidate: %s" % (item["status"], item["id"]))
    print("%s candidate validation" % report["status"])
    if report["status"] != "PASS":
        raise RuntimeError("Facial candidate validation failed")


if __name__ == "__main__":
    main()
