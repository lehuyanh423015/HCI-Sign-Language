"""Export the promoted Master Avatar v1 as a neutral static-preview GLB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_facial_glb import apply_non_armature_modifiers_keep_nmm, bake_macro_mix_keep_nmm
from rig_control_utils import sha256
from master_v1_utils import CORE_NMM


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
        raise RuntimeError(f"Expected Blender {args.expected_version}, got {bpy.app.version_string}")
    source_hash = sha256(bpy.data.filepath)
    if source_hash != args.expected_source_sha256.upper():
        raise RuntimeError("Canonical master hash mismatch")
    if bpy.context.scene.get("master_avatar_version") != "1.0.0":
        raise RuntimeError("Expected canonical Master Avatar v1.0.0")

    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or body is None:
        raise RuntimeError("Human/Human.rig missing")
    for name in CORE_NMM:
        body.data.shape_keys.key_blocks[name].value = 0.0
    bpy.context.scene.frame_set(1)

    shape_bake = bake_macro_mix_keep_nmm(body)
    modifier_bake = apply_non_armature_modifiers_keep_nmm(body)
    selected_meshes = sorted(
        (
            obj for obj in bpy.context.scene.objects
            if obj.type == "MESH" and any(mod.type == "ARMATURE" and mod.object == armature for mod in obj.modifiers)
        ),
        key=lambda item: item.name,
    )
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    armature.select_set(True)
    for obj in selected_meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = armature

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    settings = {
        "filepath": str(output),
        "export_format": "GLB",
        "use_selection": True,
        "export_animations": False,
        "export_skins": True,
        "export_armature_object_remove": True,
        "export_rest_position_armature": True,
        "export_apply": False,
        "export_all_influences": False,
        "export_morph": True,
        "export_morph_normal": True,
        "export_morph_tangent": False,
        "export_cameras": False,
        "export_lights": False,
        "export_yup": True,
    }
    result = bpy.ops.export_scene.gltf(**settings)
    report = {
        "schema_version": 1,
        "artifact": "master_avatar_v1_static_glb_export",
        "status": "PASS" if result == {"FINISHED"} and output.exists() and output.stat().st_size else "FAIL",
        "blender_version": bpy.app.version_string,
        "source": {"path": bpy.data.filepath, "sha256": source_hash},
        "selected_objects": [armature.name, *[obj.name for obj in selected_meshes]],
        "shape_key_preparation": shape_bake,
        "non_armature_modifier_bake": modifier_bake,
        "settings": settings,
        "operator_result": sorted(result),
        "output": str(output),
        "size_bytes": output.stat().st_size if output.exists() else 0,
        "sha256": sha256(output) if output.exists() else None,
        "animation_count_expected": 0,
        "technical_validation": "PENDING GLB VALIDATION",
        "owner_visual_approval": "APPROVED SOURCE",
        "linguistic_approval": "NOT YET TESTED",
    }
    Path(args.report).resolve().parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']} Master Avatar v1 static GLB: {output}")
    if report["status"] != "PASS":
        raise RuntimeError("Master Avatar v1 static export failed")


if __name__ == "__main__":
    main()
