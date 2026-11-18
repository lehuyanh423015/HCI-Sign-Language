"""Export one sign Action from a working copy to a self-contained GLB.

This script mutates only the in-memory export session and never saves the .blend.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_facial_glb import TARGETS, apply_non_armature_modifiers_keep_nmm, bake_macro_mix_keep_nmm
from rig_control_utils import sha256


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clip", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--technical-fixture", action="store_true")
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def prepare_single_nla(action, armature, shape_keys):
    rows = []
    for data_block, slot_type in ((armature, "OBJECT"), (shape_keys, "KEY")):
        animation = data_block.animation_data_create()
        animation.action = None
        for track in list(animation.nla_tracks):
            animation.nla_tracks.remove(track)
        slot = next((item for item in action.slots if item.target_id_type == slot_type), None)
        if slot is None:
            continue
        track = animation.nla_tracks.new()
        track.name = action.name
        strip = track.strips.new(action.name, int(action.frame_range[0]), action)
        strip.action_slot = slot
        rows.append({"data_block": data_block.name, "slot": slot.identifier})
    if not rows:
        raise RuntimeError(f"Action {action.name} has no OBJECT or KEY slot")
    return rows


def main():
    args = arguments()
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError(f"Expected Blender {args.expected_version}, got {bpy.app.version_string}")
    action = bpy.data.actions.get(args.clip)
    if action is None or action.frame_range[1] <= action.frame_range[0]:
        raise RuntimeError(f"Missing or invalid Action: {args.clip}")
    if not args.technical_fixture and not args.clip.startswith("S"):
        raise RuntimeError("Non-Snnn clip requires --technical-fixture")
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or body is None or body.data.shape_keys is None:
        raise RuntimeError("Human/Human.rig or Shape Keys missing")
    source = {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)}
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    bake = bake_macro_mix_keep_nmm(body)
    modifier_bake = apply_non_armature_modifiers_keep_nmm(body)
    nla = prepare_single_nla(action, armature, body.data.shape_keys)
    selected = sorted(
        (obj for obj in bpy.context.scene.objects if obj.type == "MESH" and any(mod.type == "ARMATURE" and mod.object == armature for mod in obj.modifiers)),
        key=lambda obj: obj.name,
    )
    armature.select_set(True)
    for obj in selected:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.context.scene.frame_start = int(action.frame_range[0])
    bpy.context.scene.frame_end = int(action.frame_range[1])
    bpy.context.scene.frame_set(int(action.frame_range[0]))
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    settings = {
        "filepath": str(output), "export_format": "GLB", "use_selection": True,
        "export_animations": True, "export_animation_mode": "NLA_TRACKS",
        "export_merge_animation": "NLA_TRACK", "export_frame_range": True,
        "export_force_sampling": False, "export_skins": True,
        "export_armature_object_remove": True, "export_rest_position_armature": True,
        "export_apply": False, "export_all_influences": False,
        "export_morph": True, "export_morph_normal": True, "export_morph_tangent": False,
        "export_cameras": False, "export_lights": False, "export_yup": True,
    }
    result = bpy.ops.export_scene.gltf(**settings)
    report = {
        "schema_version": 1,
        "artifact": "sign_animation_glb_export",
        "status": "PASS" if result == {"FINISHED"} and output.exists() and output.stat().st_size > 0 else "FAIL",
        "classification": "TECHNICAL_FIXTURE_NOT_A_SIGN" if args.technical_fixture else "SIGN_PRODUCTION_CANDIDATE",
        "linguistic_status": "NOT YET TESTED",
        "blender_version": bpy.app.version_string,
        "source": source,
        "clip": args.clip,
        "nla_bindings": nla,
        "shape_key_preparation": bake,
        "modifier_preparation": modifier_bake,
        "output": {"path": str(output), "sha256": sha256(output) if output.exists() else None, "size_bytes": output.stat().st_size if output.exists() else 0},
        "settings": settings,
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']} sign GLB export: {args.clip} -> {output}")
    if report["status"] != "PASS":
        raise RuntimeError("Sign GLB export failed")


if __name__ == "__main__":
    main()
