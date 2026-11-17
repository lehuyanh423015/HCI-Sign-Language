"""Export the bound character meshes + Human.rig and active technical action."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import evaluated_mesh_vertices, mesh_delta, require_rig, sha256


ACTION_NAME = "TECH_HAND_CONTROL_TEST"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--no-morphs", action="store_true", help="Exclude unverified shape keys from this technical GLB.")
    parser.add_argument("--all-influences", action="store_true", help="Export more than four skin influences per vertex.")
    parser.add_argument(
        "--detach-skinned-meshes",
        action="store_true",
        help="Detach skinned meshes from the armature parent in-memory while preserving world transforms.",
    )
    parser.add_argument(
        "--normalize-object-transforms",
        action="store_true",
        help="Apply shared object rotation/scale in-memory and verify world-space body preservation.",
    )
    parser.add_argument(
        "--remove-armature-object",
        action="store_true",
        help="Use Blender's glTF option to omit the armature object node when possible.",
    )
    parser.add_argument(
        "--bake-shape-key-mix",
        action="store_true",
        help="Bake current body shape-key values into the export-only base mesh.",
    )
    parser.add_argument(
        "--current-pose-as-rest",
        action="store_true",
        help="Use current frame pose rather than armature rest position for exported joint bind pose.",
    )
    parser.add_argument(
        "--apply-non-armature-modifiers",
        action="store_true",
        help="Apply render-visible non-armature modifiers such as MPFB's Hide helpers mask.",
    )
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

    bound_meshes = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH"
        and (
            obj.parent == armature
            or any(modifier.type == "ARMATURE" and modifier.object == armature for modifier in obj.modifiers)
        )
    ]
    if mesh not in bound_meshes:
        raise RuntimeError("Human mesh is not bound to Human.rig")

    shape_key_bake = None
    if args.bake_shape_key_mix and mesh.data.shape_keys:
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()
        before_vertices = evaluated_mesh_vertices(mesh)
        key_values = {key.name: key.value for key in mesh.data.shape_keys.key_blocks}
        for selected in bpy.context.selected_objects:
            selected.select_set(False)
        mesh.select_set(True)
        bpy.context.view_layer.objects.active = mesh
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
        bpy.context.view_layer.update()
        after_vertices = evaluated_mesh_vertices(mesh)
        preservation = mesh_delta(before_vertices, after_vertices)
        shape_key_bake = {
            "source_values": key_values,
            "body_world_mesh_delta": preservation,
            "remaining_shape_keys": 0 if mesh.data.shape_keys is None else len(mesh.data.shape_keys.key_blocks),
        }
        if preservation["max_distance"] > 1e-5:
            raise RuntimeError("Export-only shape-key bake changed evaluated body geometry")

    normalization = None
    if args.normalize_object_transforms:
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()
        before_vertices = evaluated_mesh_vertices(mesh)
        for selected in bpy.context.selected_objects:
            selected.select_set(False)
        armature.select_set(True)
        for bound_mesh in bound_meshes:
            bound_mesh.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.context.view_layer.update()
        after_vertices = evaluated_mesh_vertices(mesh)
        preservation = mesh_delta(before_vertices, after_vertices)
        normalization = {
            "body_world_mesh_delta": preservation,
            "armature_rotation": list(armature.rotation_euler),
            "armature_scale": list(armature.scale),
        }
        if preservation["max_distance"] > 1e-5:
            raise RuntimeError("Export-only transform normalization changed evaluated body geometry")

    detached_meshes = []
    if args.detach_skinned_meshes:
        for bound_mesh in bound_meshes:
            world_matrix = bound_mesh.matrix_world.copy()
            bound_mesh.parent = None
            bound_mesh.matrix_world = world_matrix
            detached_meshes.append(bound_mesh.name)

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    armature.select_set(True)
    for bound_mesh in bound_meshes:
        bound_mesh.select_set(True)
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
        export_armature_object_remove=args.remove_armature_object,
        export_rest_position_armature=not args.current_pose_as_rest,
        export_apply=args.apply_non_armature_modifiers,
        export_all_influences=args.all_influences,
        export_morph=not args.no_morphs,
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
        "morph_targets_exported": not args.no_morphs,
        "all_skin_influences_exported": args.all_influences,
        "detached_skinned_meshes_for_export": sorted(detached_meshes),
        "export_only_transform_normalization": normalization,
        "armature_object_removed_by_exporter": args.remove_armature_object,
        "export_only_shape_key_bake": shape_key_bake,
        "current_pose_used_as_export_rest": args.current_pose_as_rest,
        "non_armature_modifiers_applied": args.apply_non_armature_modifiers,
        "selected_objects": sorted([armature.name] + [item.name for item in bound_meshes]),
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
