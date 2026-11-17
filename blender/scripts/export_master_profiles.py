"""Export verified TASK-0005 MASTER_STATIC and diagnostic MORPH_POC profiles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import evaluated_mesh_vertices, mesh_delta, sha256


PROFILES = {"MASTER_STATIC", "MORPH_POC"}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, choices=sorted(PROFILES))
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def bake_body_shape_mix(body):
    if not body.data.shape_keys:
        return {"shape_keys_before": 0, "status": "SKIPPED"}
    values = {key.name: key.value for key in body.data.shape_keys.key_blocks}
    before = evaluated_mesh_vertices(body)
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
    bpy.context.view_layer.update()
    after = evaluated_mesh_vertices(body)
    delta = mesh_delta(before, after)
    if delta["max_distance"] > 1e-6:
        raise RuntimeError("Baking current shape mix changed evaluated world geometry")
    return {
        "shape_keys_before": len(values),
        "values_before": values,
        "shape_keys_after": 0 if body.data.shape_keys is None else len(body.data.shape_keys.key_blocks),
        "evaluated_world_delta": delta,
        "status": "PASS",
    }


def create_morph_probe():
    vertices = [
        (-0.025, -0.025, -0.025), (0.025, -0.025, -0.025),
        (0.025, 0.025, -0.025), (-0.025, 0.025, -0.025),
        (-0.025, -0.025, 0.025), (0.025, -0.025, 0.025),
        (0.025, 0.025, 0.025), (-0.025, 0.025, 0.025),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7),
    ]
    mesh_data = bpy.data.meshes.new("TASK0005_MorphProbeMesh")
    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update()
    probe = bpy.data.objects.new("TASK0005_MorphProbe", mesh_data)
    bpy.context.collection.objects.link(probe)
    probe.location = (0.0, 0.0, 1.9)
    probe["diagnostic_only"] = True
    probe.shape_key_add(name="Basis")
    key = probe.shape_key_add(name="TASK0005_DIAGNOSTIC_MORPH")
    for index in (4, 5, 6, 7):
        key.data[index].co.z += 0.05
    key.slider_min = 0.0
    key.slider_max = 1.0
    for frame, value in ((1, 0.0), (15, 1.0), (30, 0.0)):
        key.value = value
        key.keyframe_insert(data_path="value", frame=frame)
    action = probe.data.shape_keys.animation_data.action
    action.name = "TASK0005_DIAGNOSTIC_MORPH"
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 30
    bpy.context.scene.render.fps = 30
    return probe, action


def exporter_properties():
    return sorted(
        prop.identifier for prop in bpy.ops.export_scene.gltf.get_rna_type().properties
        if prop.identifier != "rna_type"
    )


def main():
    args = arguments()
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    output = Path(args.output).resolve()
    report_path = Path(args.report).resolve()
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or body is None:
        raise RuntimeError("Human/Human.rig not found")

    source = {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)}
    bound_meshes = sorted(
        [
            obj for obj in bpy.data.objects if obj.type == "MESH"
            and any(mod.type == "ARMATURE" and mod.object == armature for mod in obj.modifiers)
        ],
        key=lambda item: item.name,
    )
    if {mesh.name for mesh in bound_meshes} != {"Human", "EDU_NeutralTop", "EDU_NeutralShorts"}:
        raise RuntimeError("Unexpected canonical bound mesh set: %s" % ", ".join(mesh.name for mesh in bound_meshes))

    shape_bake = bake_body_shape_mix(body)
    probe = None
    diagnostic_action = None
    if args.profile == "MASTER_STATIC":
        if bpy.data.actions:
            raise RuntimeError("MASTER_STATIC source must not contain actions")
    else:
        if bpy.data.actions.get("TECH_HAND_CONTROL_TEST") is None:
            raise RuntimeError("MORPH_POC requires TECH_HAND_CONTROL_TEST bone animation")
        probe, diagnostic_action = create_morph_probe()

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    selected = [armature, *bound_meshes]
    if probe:
        selected.append(probe)
    for obj in selected:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = armature

    animations = args.profile == "MORPH_POC"
    morphs = args.profile == "MORPH_POC"
    settings = {
        "filepath": str(output),
        "export_format": "GLB",
        "use_selection": True,
        "export_animations": animations,
        "export_animation_mode": "ACTIONS",
        "export_merge_animation": "ACTION",
        "export_frame_range": True,
        "export_force_sampling": False,
        "export_skins": True,
        "export_armature_object_remove": True,
        "export_rest_position_armature": True,
        "export_apply": True,
        "export_all_influences": False,
        "export_morph": morphs,
        "export_morph_normal": morphs,
        "export_morph_tangent": False,
        "export_cameras": False,
        "export_lights": False,
        "export_yup": True,
    }
    supported = exporter_properties()
    unsupported = sorted(key for key in settings if key not in supported and key != "filepath")
    if unsupported:
        raise RuntimeError("Unsupported Blender 5.2 glTF options: %s" % ", ".join(unsupported))

    output.parent.mkdir(parents=True, exist_ok=True)
    result = bpy.ops.export_scene.gltf(**settings)
    report = {
        "schema_version": 1,
        "artifact": "master_avatar_glb_export",
        "profile": args.profile,
        "diagnostic_only": args.profile == "MORPH_POC",
        "blender_version": bpy.app.version_string,
        "source": source,
        "selected_objects": sorted(obj.name for obj in selected),
        "source_actions_at_export": sorted(action.name for action in bpy.data.actions),
        "diagnostic_morph_action": diagnostic_action.name if diagnostic_action else None,
        "shape_key_mix_bake": shape_bake,
        "verified_exporter_properties": supported,
        "settings": settings,
        "operator_result": sorted(result),
        "output": str(output),
        "size_bytes": output.stat().st_size if output.exists() else 0,
        "sha256": sha256(output) if output.exists() else None,
        "status": "PASS" if result == {"FINISHED"} and output.exists() and output.stat().st_size > 0 else "FAIL",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("[%s] %s export: %s" % (report["status"], args.profile, output))
    print("JSON report: %s" % report_path)
    if report["status"] != "PASS":
        raise RuntimeError("Master profile export failed")


if __name__ == "__main__":
    main()
