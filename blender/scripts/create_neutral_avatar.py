"""Create a modest, neutral educational avatar on a separate working copy."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import action_fcurves, matrix_signature, require_rig, sha256


ACTION_NAME = "TECH_HAND_CONTROL_TEST"
GARMENT_NAMES = ("EDU_NeutralTop", "EDU_NeutralShorts")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-output", required=True)
    parser.add_argument("--candidate-output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--preview-directory", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def make_material(name: str, color: tuple[float, float, float, float], roughness: float):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    material.surface_render_method = "DITHERED"
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = 0.0
    return material


def append_elliptical_tube(vertices, faces, rings, segments=32):
    first = len(vertices)
    for center, radius_x, radius_y in rings:
        for index in range(segments):
            angle = 2.0 * 3.141592653589793 * index / segments
            vertices.append(
                (
                    center.x + radius_x * math.cos(angle),
                    center.y + radius_y * math.sin(angle),
                    center.z,
                )
            )
    for ring_index in range(len(rings) - 1):
        lower = first + ring_index * segments
        upper = lower + segments
        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append((lower + index, lower + next_index, upper + next_index, upper + index))


def append_limb_tube(vertices, faces, start, end, start_radius, end_radius, segments=24):
    axis = (end - start).normalized()
    reference = Vector((0.0, 0.0, 1.0))
    if abs(axis.dot(reference)) > 0.9:
        reference = Vector((0.0, 1.0, 0.0))
    basis_x = axis.cross(reference).normalized()
    basis_y = axis.cross(basis_x).normalized()
    first = len(vertices)
    for center, radius in ((start, start_radius), (end, end_radius)):
        for index in range(segments):
            angle = 2.0 * 3.141592653589793 * index / segments
            point = center + basis_x * (math.cos(angle) * radius) + basis_y * (math.sin(angle) * radius)
            vertices.append(tuple(point))
    for index in range(segments):
        next_index = (index + 1) % segments
        faces.append((first + index, first + next_index, first + segments + next_index, first + segments + index))


def transfer_body_weights(body, garment):
    for source_group in body.vertex_groups:
        garment.vertex_groups.new(name=source_group.name)
    transfer = garment.modifiers.new("Transfer body weights", "DATA_TRANSFER")
    transfer.object = body
    transfer.use_vert_data = True
    transfer.data_types_verts = {"VGROUP_WEIGHTS"}
    transfer.vert_mapping = "POLYINTERP_NEAREST"
    transfer.layers_vgroup_select_src = "ALL"
    transfer.layers_vgroup_select_dst = "NAME"
    bpy.context.view_layer.objects.active = garment
    garment.select_set(True)
    body.select_set(False)
    bpy.ops.object.modifier_apply(modifier=transfer.name)


def create_garment(body, armature, name, material, geometry_builder):
    vertices = []
    faces = []
    geometry_builder(vertices, faces)
    mesh = bpy.data.meshes.new("%s_Mesh" % name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    garment = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(garment)
    garment.data.materials.append(material)
    garment.parent = armature
    garment.matrix_world = body.matrix_world.copy()
    transfer_body_weights(body, garment)
    armature_modifier = garment.modifiers.new("Armature", "ARMATURE")
    armature_modifier.object = armature
    armature_modifier.use_vertex_groups = True
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return garment


def rig_signature(armature):
    return [
        {"name": bone.name, "parent": bone.parent.name if bone.parent else None, "deform": bone.use_deform}
        for bone in armature.data.bones
    ]


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_previews(scene, body, armature, preview_directory: Path, prefix: str, frames, close_up=False):
    preview_directory.mkdir(parents=True, exist_ok=True)
    original_camera = scene.camera
    camera_data = bpy.data.cameras.new("TASK0004_PREVIEW_CAMERA_DATA")
    camera = bpy.data.objects.new("TASK0004_PREVIEW_CAMERA", camera_data)
    scene.collection.objects.link(camera)

    if close_up:
        scene.frame_set(15)
        bpy.context.view_layer.update()
        points = [armature.matrix_world @ armature.pose.bones[name].head for name in ("wrist.R", "finger2-1.R", "finger5-1.R")]
        target = sum(points, Vector()) / len(points)
        camera.location = target + body.matrix_world.to_quaternion() @ Vector((0.0, -0.52, 0.08))
        camera_data.lens = 58
    else:
        target = body.matrix_world @ Vector((0.0, -0.04, 0.83))
        camera.location = body.matrix_world @ Vector((0.0, -3.05, 0.86))
        camera_data.lens = 58
    camera_data.clip_start = 0.01
    look_at(camera, target)
    scene.camera = camera

    light_specs = [
        ("KEY", 900, Vector((-1.8, -2.0, 3.2)), 2.5),
        ("FILL", 500, Vector((1.8, -1.2, 2.0)), 2.0),
        ("RIM", 650, Vector((0.0, 1.5, 2.5)), 1.8),
    ]
    light_objects = []
    light_data_blocks = []
    for suffix, energy, local_position, size in light_specs:
        data = bpy.data.lights.new("TASK0004_%s_DATA" % suffix, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new("TASK0004_%s" % suffix, data)
        scene.collection.objects.link(light)
        light.location = body.matrix_world @ local_position
        look_at(light, target)
        light_objects.append(light)
        light_data_blocks.append(data)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900 if not close_up else 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.025, 0.035, 0.033)
    outputs = []
    for frame in frames:
        scene.frame_set(frame)
        output = preview_directory / ("%s-frame-%03d.png" % (prefix, frame))
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        outputs.append({"frame": frame, "path": str(output), "sha256": sha256(output)})

    scene.camera = original_camera
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    for light in light_objects:
        bpy.data.objects.remove(light, do_unlink=True)
    for data in light_data_blocks:
        bpy.data.lights.remove(data)
    return outputs


def garment_record(garment):
    coordinates = [vertex.co for vertex in garment.data.vertices]
    bounds_min = [min(point[index] for point in coordinates) for index in range(3)]
    bounds_max = [max(point[index] for point in coordinates) for index in range(3)]
    weighted_vertices = sum(1 for vertex in garment.data.vertices if vertex.groups)
    return {
        "name": garment.name,
        "vertices": len(garment.data.vertices),
        "polygons": len(garment.data.polygons),
        "weighted_vertices": weighted_vertices,
        "bounds_local": {"min": bounds_min, "max": bounds_max},
        "materials": [slot.material.name if slot.material else None for slot in garment.material_slots],
        "modifiers": [{"name": modifier.name, "type": modifier.type} for modifier in garment.modifiers],
    }


def main():
    args = arguments()
    armature, body = require_rig()
    source_path = Path(bpy.data.filepath).resolve()
    source_hash = sha256(source_path)
    source_rig = rig_signature(armature)
    source_armature_transform = matrix_signature(armature.matrix_world)

    preview_directory = Path(args.preview_directory).resolve()
    before_previews = render_previews(
        bpy.context.scene,
        body,
        armature,
        preview_directory,
        "before-neutralization-full",
        (1,),
    )

    for name in GARMENT_NAMES:
        previous = bpy.data.objects.get(name)
        if previous:
            bpy.data.objects.remove(previous, do_unlink=True)

    skin = make_material("EDU_Skin_Neutral", (0.52, 0.49, 0.45, 1.0), 0.78)
    top_material = make_material("EDU_Top_Teal", (0.035, 0.20, 0.18, 1.0), 0.68)
    shorts_material = make_material("EDU_Shorts_Slate", (0.035, 0.055, 0.075, 1.0), 0.72)
    body.data.materials.clear()
    body.data.materials.append(skin)

    def top_geometry(vertices, faces):
        append_elliptical_tube(
            vertices,
            faces,
            [
                (Vector((0.0, -0.025, 0.975)), 0.205, 0.155),
                (Vector((0.0, -0.025, 1.18)), 0.210, 0.160),
                (Vector((0.0, -0.025, 1.335)), 0.245, 0.170),
                (Vector((0.0, -0.020, 1.405)), 0.105, 0.105),
            ],
        )
        for side in ("L", "R"):
            upper = armature.data.bones["upperarm01.%s" % side]
            elbow = armature.data.bones["lowerarm01.%s" % side].head_local
            start = upper.head_local.lerp(elbow, 0.04)
            end = upper.head_local.lerp(elbow, 0.62)
            append_limb_tube(vertices, faces, start, end, 0.084, 0.072)

    def shorts_geometry(vertices, faces):
        append_elliptical_tube(
            vertices,
            faces,
            [
                (Vector((0.0, -0.020, 1.03)), 0.205, 0.165),
                (Vector((0.0, -0.020, 0.89)), 0.225, 0.180),
                (Vector((0.0, -0.020, 0.79)), 0.205, 0.170),
            ],
        )
        for center_x in (-0.105, 0.105):
            append_elliptical_tube(
                vertices,
                faces,
                [
                    (Vector((center_x, -0.015, 0.86)), 0.125, 0.160),
                    (Vector((center_x, -0.015, 0.62)), 0.115, 0.145),
                ],
            )
        # Front/back modesty panels bridge the leg tubes without exposing the body.
        first = len(vertices)
        vertices.extend(
            [
                (-0.13, -0.202, 0.88),
                (0.13, -0.202, 0.88),
                (0.11, -0.175, 0.62),
                (-0.11, -0.175, 0.62),
                (-0.13, 0.155, 0.88),
                (-0.11, 0.135, 0.62),
                (0.11, 0.135, 0.62),
                (0.13, 0.155, 0.88),
            ]
        )
        faces.extend(((first, first + 1, first + 2, first + 3), (first + 4, first + 5, first + 6, first + 7)))

    top = create_garment(body, armature, GARMENT_NAMES[0], top_material, top_geometry)
    shorts = create_garment(body, armature, GARMENT_NAMES[1], shorts_material, shorts_geometry)

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 30
    scene.frame_set(1)
    bpy.context.view_layer.update()

    after_full = render_previews(scene, body, armature, preview_directory, "neutral-avatar-full", (1, 15, 30))
    after_hand = render_previews(scene, body, armature, preview_directory, "neutral-avatar-hand", (1, 15, 30), close_up=True)
    scene.frame_set(1)

    working_output = Path(args.working_output).resolve()
    candidate_output = Path(args.candidate_output).resolve()
    working_output.parent.mkdir(parents=True, exist_ok=True)
    candidate_output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(working_output), check_existing=False)
    working_hash = sha256(working_output)
    bpy.ops.wm.save_as_mainfile(filepath=str(candidate_output), check_existing=False)
    candidate_hash = sha256(candidate_output)

    action = bpy.data.actions.get(ACTION_NAME)
    slot = next((item for item in action.slots if item.target_id_type == "OBJECT"), None) if action else None
    curves = list(action_fcurves(action, slot)) if action and slot else []
    animated_bones = sorted(
        {
            curve.data_path.split('pose.bones["', 1)[1].split('"]', 1)[0]
            for curve in curves
            if 'pose.bones["' in curve.data_path
        }
    )
    checks = {
        "source_not_overwritten": source_path not in (working_output, candidate_output) and sha256(source_path) == source_hash,
        "rig_hierarchy_preserved": source_rig == rig_signature(armature),
        "armature_object_transform_preserved": source_armature_transform == matrix_signature(armature.matrix_world),
        "technical_action_preserved": action is not None and len(curves) == 45 and len(animated_bones) == 15,
        "body_material_neutralized": body.active_material is not None and body.active_material.name == skin.name,
        "garments_created": all(bpy.data.objects.get(name) is not None for name in GARMENT_NAMES),
        "garments_weighted": all(all(vertex.groups for vertex in garment.data.vertices) for garment in (top, shorts)),
    }
    report = {
        "schema_version": 1,
        "artifact": "neutral_educational_avatar_creation",
        "technical_fixture_only": True,
        "blender_version": bpy.app.version_string,
        "source": {"path": str(source_path), "sha256": source_hash},
        "strategy": "procedural low-detail garment shells with transferred body weights and no textures",
        "materials": {
            "body": skin.name,
            "top": top_material.name,
            "shorts": shorts_material.name,
            "textures": [],
        },
        "garments": [garment_record(top), garment_record(shorts)],
        "action": {"name": action.name if action else None, "fcurve_count": len(curves), "animated_bones": animated_bones},
        "outputs": {
            "working": {"path": str(working_output), "sha256": working_hash},
            "candidate": {"path": str(candidate_output), "sha256": candidate_hash},
        },
        "previews": {"before": before_previews, "after_full": after_full, "after_hand": after_hand},
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print("[%s] %s" % ("PASS" if passed else "FAIL", name))
    print("[%s] neutral educational avatar created" % report["status"])
    print("Working source: %s" % working_output)
    print("Master candidate: %s" % candidate_output)
    print("JSON report: %s" % report_path)
    if report["status"] != "PASS":
        raise RuntimeError("Neutral avatar creation checks failed")


if __name__ == "__main__":
    main()
