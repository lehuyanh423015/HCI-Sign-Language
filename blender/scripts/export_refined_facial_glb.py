"""Export TASK-0007A refined facial candidate to a separate technical GLB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_facial_glb import (
    ACTIONS, TARGETS, apply_non_armature_modifiers_keep_nmm,
    bake_macro_mix_keep_nmm, prepare_nla_tracks,
)
from rig_control_utils import sha256


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def main():
    args = arguments()
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    source_hash = sha256(bpy.data.filepath)
    if source_hash != args.expected_source_sha256.upper():
        raise RuntimeError("Refined candidate hash mismatch")
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if not armature or not body:
        raise RuntimeError("Human/Human.rig missing")
    if bpy.context.scene.get("master_avatar_version") != "1.0.0-rc.3":
        raise RuntimeError("Expected refined candidate rc.3")
    missing_actions = [name for name in ACTIONS if bpy.data.actions.get(name) is None]
    if missing_actions:
        raise RuntimeError("Missing actions: %s" % ", ".join(missing_actions))

    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    bake = bake_macro_mix_keep_nmm(body)
    bake["mode"] = "refined_macro_mix_baked_in_memory_then_nmm_targets_recreated"
    modifier_bake = apply_non_armature_modifiers_keep_nmm(body)
    nla_tracks = prepare_nla_tracks(armature, body.data.shape_keys)
    selected = sorted([
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and any(mod.type == "ARMATURE" and mod.object == armature for mod in obj.modifiers)
    ], key=lambda obj: obj.name)
    expected = {
        "Human", "EDU_NeutralTop", "EDU_NeutralShorts",
        "NMM_Eyeball.L", "NMM_Iris.L", "NMM_Pupil.L",
        "NMM_Eyeball.R", "NMM_Iris.R", "NMM_Pupil.R",
    }
    if {obj.name for obj in selected} != expected:
        raise RuntimeError("Unexpected selected mesh set: %s" % ", ".join(obj.name for obj in selected))
    armature.select_set(True)
    for obj in selected:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.context.scene.frame_set(1)

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    settings = {
        "filepath": str(output), "export_format": "GLB", "use_selection": True,
        "export_animations": True, "export_animation_mode": "NLA_TRACKS",
        "export_merge_animation": "NLA_TRACK", "export_frame_range": True,
        "export_force_sampling": False, "export_skins": True,
        "export_armature_object_remove": True, "export_rest_position_armature": True,
        "export_apply": False, "export_all_influences": False,
        "export_morph": True, "export_morph_normal": True,
        "export_morph_tangent": False, "export_cameras": False,
        "export_lights": False, "export_yup": True,
    }
    result = bpy.ops.export_scene.gltf(**settings)
    report = {
        "schema_version": 1, "artifact": "task0007a_refined_facial_glb_export",
        "technical_fixture_only": True, "linguistic_status": "NOT YET TESTED",
        "blender_version": bpy.app.version_string,
        "source": {"path": bpy.data.filepath, "sha256": source_hash},
        "selected_objects": [armature.name] + [obj.name for obj in selected],
        "actions": list(ACTIONS), "nla_tracks": nla_tracks,
        "shape_key_preparation": bake, "non_armature_modifier_bake": modifier_bake,
        "settings": settings, "operator_result": sorted(result),
        "output": str(output), "size_bytes": output.stat().st_size if output.exists() else 0,
        "sha256": sha256(output) if output.exists() else None,
    }
    report["status"] = "PASS" if result == {"FINISHED"} and report["size_bytes"] > 0 else "FAIL"
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("%s refined facial GLB: %s" % (report["status"], output))
    if report["status"] != "PASS":
        raise RuntimeError("Refined facial GLB export failed")


if __name__ == "__main__":
    main()
