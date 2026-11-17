"""Export the TASK-0006 facial candidate to a technical GLB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import sha256


TARGETS = (
    "NMM_BROW_RAISE_L", "NMM_BROW_RAISE_R", "NMM_EYE_BLINK_L",
    "NMM_EYE_BLINK_R", "NMM_LIPS_ROUND", "NMM_LIPS_SPREAD",
)
ACTIONS = ("NMM_BLINK_TEST", "NMM_BROW_TEST", "NMM_MOUTH_TEST", "TECH_HAND_FACE_TEST")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def bake_macro_mix_keep_nmm(body):
    keys = body.data.shape_keys.key_blocks
    basis = body.data.shape_keys.reference_key
    deltas = {name: [key.co - base.co for key, base in zip(keys[name].data, basis.data)] for name in TARGETS}
    source_values = {key.name: key.value for key in keys}
    for name in TARGETS:
        keys[name].value = 0.0
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
    new_basis = body.shape_key_add(name="Basis", from_mix=False)
    for name in TARGETS:
        key = body.shape_key_add(name=name, from_mix=False)
        key.slider_min = 0.0
        key.slider_max = 1.0
        for index, delta in enumerate(deltas[name]):
            key.data[index].co = new_basis.data[index].co + delta
    return {"source_values": source_values, "export_targets": list(TARGETS), "vertex_count": len(body.data.vertices)}


def apply_non_armature_modifiers_keep_nmm(body):
    """Evaluate the mask once per target and rebuild an export-only Key datablock."""
    armature_modifiers = [modifier for modifier in body.modifiers if modifier.type == "ARMATURE"]
    non_armature_modifiers = [modifier for modifier in body.modifiers if modifier.type != "ARMATURE"]
    modifier_names = [modifier.name for modifier in non_armature_modifiers]
    if not non_armature_modifiers:
        return {"status": "SKIPPED", "modifiers": [], "vertices_before": len(body.data.vertices), "vertices_after": len(body.data.vertices)}
    for modifier in armature_modifiers:
        modifier.show_viewport = False
        modifier.show_render = False
    keys = body.data.shape_keys.key_blocks
    for name in TARGETS:
        keys[name].value = 0.0
    depsgraph = bpy.context.evaluated_depsgraph_get()

    def evaluated_mesh(name):
        bpy.context.view_layer.update()
        mesh = bpy.data.meshes.new_from_object(body.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)
        mesh.name = name
        return mesh

    vertices_before = len(body.data.vertices)
    base_mesh = evaluated_mesh("TASK0006_ExportBase")
    target_coordinates = {}
    for name in TARGETS:
        keys[name].value = 1.0
        target_mesh = evaluated_mesh("TASK0006_%s" % name)
        if len(target_mesh.vertices) != len(base_mesh.vertices):
            raise RuntimeError("Modifier topology differs for %s" % name)
        target_coordinates[name] = [vertex.co.copy() for vertex in target_mesh.vertices]
        bpy.data.meshes.remove(target_mesh)
        keys[name].value = 0.0
    old_mesh = body.data
    body.data = base_mesh
    for modifier in non_armature_modifiers:
        body.modifiers.remove(modifier)
    for modifier in armature_modifiers:
        modifier.show_viewport = True
        modifier.show_render = True
    basis = body.shape_key_add(name="Basis", from_mix=False)
    for name in TARGETS:
        key = body.shape_key_add(name=name, from_mix=False)
        key.slider_min = 0.0
        key.slider_max = 1.0
        for index, coordinate in enumerate(target_coordinates[name]):
            key.data[index].co = coordinate
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    weighted = sum(bool(vertex.groups) for vertex in body.data.vertices)
    if weighted != len(body.data.vertices):
        raise RuntimeError("Mask rebuild lost body skin weights: %d/%d" % (weighted, len(body.data.vertices)))
    return {
        "status": "PASS", "modifiers": modifier_names,
        "vertices_before": vertices_before, "vertices_after": len(body.data.vertices),
        "fully_weighted_vertices": weighted,
    }


def prepare_nla_tracks(armature, shape_keys):
    armature_animation = armature.animation_data_create()
    shape_animation = shape_keys.animation_data_create()
    armature_animation.action = None
    shape_animation.action = None
    for animation in (armature_animation, shape_animation):
        for track in list(animation.nla_tracks):
            animation.nla_tracks.remove(track)
    rows = []
    for name in ACTIONS:
        action = bpy.data.actions[name]
        object_slot = next(slot for slot in action.slots if slot.target_id_type == "OBJECT")
        key_slot = next(slot for slot in action.slots if slot.target_id_type == "KEY")
        start = int(action.frame_range[0])
        object_track = armature_animation.nla_tracks.new()
        object_track.name = name
        object_strip = object_track.strips.new(name, start, action)
        object_strip.action_slot = object_slot
        key_track = shape_animation.nla_tracks.new()
        key_track.name = name
        key_strip = key_track.strips.new(name, start, action)
        key_strip.action_slot = key_slot
        rows.append({"name": name, "object_slot": object_slot.identifier, "key_slot": key_slot.identifier})
    return rows


def main():
    args = arguments()
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if not armature or not body:
        raise RuntimeError("Human/Human.rig missing")
    missing_actions = [name for name in ACTIONS if bpy.data.actions.get(name) is None]
    if missing_actions:
        raise RuntimeError("Missing actions: %s" % ", ".join(missing_actions))
    source = {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)}
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    bake = bake_macro_mix_keep_nmm(body)
    bake["mode"] = "macro_mix_baked_in_memory_then_nmm_targets_recreated"
    bake["additional_mpfb_targets_unapproved"] = []
    modifier_bake = apply_non_armature_modifiers_keep_nmm(body)
    nla_tracks = prepare_nla_tracks(armature, body.data.shape_keys)
    selected = sorted([
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and any(mod.type == "ARMATURE" and mod.object == armature for mod in obj.modifiers)
    ], key=lambda obj: obj.name)
    expected = {"Human", "EDU_NeutralTop", "EDU_NeutralShorts", "NMM_Eyeball.L", "NMM_Iris.L", "NMM_Pupil.L", "NMM_Eyeball.R", "NMM_Iris.R", "NMM_Pupil.R"}
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
        "schema_version": 1, "artifact": "task0006_facial_glb_export",
        "technical_fixture_only": True, "linguistic_status": "NOT YET TESTED",
        "blender_version": bpy.app.version_string, "source": source,
        "selected_objects": [armature.name] + [obj.name for obj in selected],
        "actions": list(ACTIONS), "nla_tracks": nla_tracks, "shape_key_preparation": bake,
        "non_armature_modifier_bake": modifier_bake,
        "settings": settings, "operator_result": sorted(result),
        "output": str(output), "size_bytes": output.stat().st_size if output.exists() else 0,
        "sha256": sha256(output) if output.exists() else None,
    }
    report["status"] = "PASS" if result == {"FINISHED"} and report["size_bytes"] > 0 else "FAIL"
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("[%s] facial GLB: %s (%d bytes)" % (report["status"], output, report["size_bytes"]))
    if report["status"] != "PASS":
        raise RuntimeError("Facial GLB export failed")


if __name__ == "__main__":
    main()
