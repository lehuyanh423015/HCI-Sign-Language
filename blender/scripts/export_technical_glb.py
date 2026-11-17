"""Export only Human + Human.rig and the active technical action to GLB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import require_rig, sha256


ACTION_NAME = "TECH_HAND_CONTROL_TEST"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def main():
    args = arguments()
    armature, mesh = require_rig()
    action = bpy.data.actions.get(ACTION_NAME)
    if action is None:
        raise RuntimeError("Expected action %s was not found" % ACTION_NAME)
    if not armature.animation_data or armature.animation_data.action != action:
        raise RuntimeError("Expected action is not active on Human.rig")

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    armature.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = armature

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    result = bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_animation_mode="ACTIONS",
        export_merge_animation="ACTION",
        export_frame_range=True,
        export_force_sampling=False,
        export_skins=True,
        export_all_influences=True,
        export_morph=True,
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )
    report = {
        "schema_version": 1,
        "artifact": "technical_hand_test_glb_export",
        "technical_fixture_only": True,
        "blender_version": bpy.app.version_string,
        "source_blend": bpy.data.filepath,
        "action": action.name,
        "selected_objects": sorted([armature.name, mesh.name]),
        "operator_result": sorted(result),
        "output": str(output),
        "size_bytes": output.stat().st_size if output.exists() else 0,
        "sha256": sha256(output) if output.exists() else None,
        "status": "PASS" if result == {"FINISHED"} and output.exists() and output.stat().st_size > 0 else "FAIL",
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("[%s] GLB export: %s (%d bytes)" % (report["status"], output, report["size_bytes"]))
    print("JSON report: %s" % report_path)
    if report["status"] != "PASS":
        raise RuntimeError("GLB export failed")


if __name__ == "__main__":
    main()
