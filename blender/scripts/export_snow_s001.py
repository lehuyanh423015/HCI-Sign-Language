"""Retarget the existing S001 technical draft to Snow and export the web GLB."""

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preview_snow_hand_poses import FINGERS

CLIP = "S001_MAIN"
SIDES = ("L", "R")
SKIN_MESHES = ("GEO-snow-body", "GEO-snow-head")
TEXTURED_MESHES = {
    "GEO-snow-shirt": "shirt",
    "GEO-snow-pants": "pants",
    "GEO-snow-shoes_base": "shoes",
    "GEO-snow-shoes_bottom": "shoes",
    "GEO-snow-shoes_parts": "shoes",
    "GEO-snow-hair_base": "hair",
    "GEO-snow-eyebrows": "hair",
    "GEO-snow-eyes": "eyes",
}
DETAIL_MESHES = ("GEO-snow-teeth_upper", "GEO-snow-teeth_lower", "GEO-snow-gums_upper",
                 "GEO-snow-gums_lower", "GEO-snow-tongue")
GATHER_FRAME = 5
GATHER_FINGER_SCALE = 0.78


def palm_basis(bones, wrist, index, pinky, rest=False):
    points = [bones[name].bone.head_local if rest else bones[name].head for name in (wrist, index, pinky)]
    wrist, index, pinky = points
    across = (index - pinky).normalized()
    normal = across.cross((index + pinky) * 0.5 - wrist).normalized()
    forward = normal.cross(across).normalized()
    return Matrix((across, forward, normal)).transposed().to_quaternion()


def source_animation(path, scene):
    with bpy.data.libraries.load(str(path)) as (library, linked):
        if "Human.rig" not in library.objects:
            raise RuntimeError(f"Missing Human.rig in {path}")
        linked.objects = ["Human.rig"]
    source, = linked.objects
    scene.collection.objects.link(source)
    action = source.animation_data.action
    if action.name != CLIP:
        raise RuntimeError(f"Expected {CLIP}, found {action.name}")
    action.name = "Source S001"
    start, end = map(round, action.frame_range)
    bones = source.pose.bones
    rest = {bone.name: bone.bone.matrix_local.to_quaternion() for bone in bones}
    frames = {}
    for frame in range(start, end + 1):
        scene.frame_set(frame)
        frames[frame] = {
            "rotations": {bone.name: bone.matrix.to_quaternion() for bone in bones},
            "palms": {
                side: palm_basis(bones, f"wrist.{side}", f"finger2-1.{side}", f"finger5-1.{side}")
                for side in SIDES
            },
        }
    bpy.data.objects.remove(source, do_unlink=True)
    return frames, rest


def key_rotation(bone, frame, quaternion):
    bone.rotation_mode = "QUATERNION"
    if bone.rotation_quaternion.dot(quaternion) < 0:
        quaternion.negate()
    bone.rotation_quaternion = quaternion
    bone.keyframe_insert("rotation_quaternion", frame=frame, group=bone.name)


def key_absolute(bone, frame, rotation):
    bpy.context.view_layer.update()
    current = bone.matrix.to_quaternion()
    local = bone.matrix_basis.to_quaternion()
    key_rotation(bone, frame, local @ current.inverted() @ rotation)


def retarget(rig, scene, frames, source_rest):
    rig.animation_data_create().action = None
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    bones = rig.pose.bones
    properties = bones["Properties"]
    for side in ("left", "right"):
        properties[f"ik_{side}_upperarm"] = 0.0
    rig.update_tag()
    bpy.context.view_layer.update()
    target_rest = {bone.name: bone.bone.matrix_local.to_quaternion() for bone in bones}
    mappings = {}
    for side in SIDES:
        wrist = f"FK-Wrist.{side}"
        target_palm = palm_basis(bones, wrist, f"FK-Finger_Index1.{side}", f"FK-Finger_Pinky1.{side}", rest=True)
        wrist_offset = target_palm.inverted() @ target_rest[wrist]
        arms = []
        for src, dst in (("upperarm01", "FK-UpperArm"), ("lowerarm01", "FK-Forearm")):
            src, dst = f"{src}.{side}", f"{dst}.{side}"
            y = Vector((0.0, 1.0, 0.0))
            source_direction = source_rest[src] @ y
            target_direction = target_rest[dst] @ y
            offset = source_rest[src].inverted() @ target_direction.rotation_difference(source_direction) @ target_rest[dst]
            arms.append((src, dst, offset))
        fingers = []
        reference = frames[min(frames)]["rotations"]
        for index, finger in enumerate(FINGERS, 1):
            for joint in (1, 2, 3):
                src = f"finger{index}-{joint}.{side}"
                parent = f"finger{index}-{joint - 1}.{side}" if joint > 1 else f"wrist.{side}"
                dst = f"FK-Finger_{finger}{joint}.{side}"
                neutral = reference[parent].inverted() @ reference[src]
                source_palm = frames[min(frames)]["palms"][side]
                offset = reference[src].inverted() @ source_palm @ target_palm.inverted() @ target_rest[dst]
                fingers.append((src, parent, dst, neutral, offset, finger))
        mappings[side] = (arms, wrist, wrist_offset, fingers)

    scene.frame_start, scene.frame_end = min(frames), max(frames)
    scene.render.fps, scene.render.fps_base = 30, 1.0
    for frame, sample in frames.items():
        scene.frame_set(frame)
        rotations = sample["rotations"]
        for side, (arms, wrist, wrist_offset, fingers) in mappings.items():
            for src, dst, offset in arms:
                key_absolute(bones[dst], frame, rotations[src] @ offset)
            key_absolute(bones[wrist], frame, sample["palms"][side] @ wrist_offset)
            for src, parent, dst, neutral, offset, finger in fingers:
                delta = neutral.inverted() @ rotations[parent].inverted() @ rotations[src]
                local = offset.inverted() @ delta @ offset
                # The source gather pose intersects Snow's index and middle fingertips.
                if frame == GATHER_FRAME and finger in ("Index", "Middle"):
                    local = Quaternion().slerp(local, GATHER_FINGER_SCALE)
                key_rotation(bones[dst], frame, local)
    rig.animation_data.action.name = CLIP
    scene.frame_set(scene.frame_start)


def web_material(directory, name, tile=None):
    suffix = f".{tile}" if tile else ""
    material = bpy.data.materials.new(f"Snow {name}{suffix}")
    material.use_nodes = True
    tree = material.node_tree
    shader = tree.nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value = 0.28 if name == "eyes" else 0.55
    for kind, socket in (("diffuse", "Base Color"), ("roughness", "Roughness"),
                         ("normal", "Normal"), ("metalness", "Metallic")):
        path = directory / f"{name}_{kind}{suffix}.png"
        if not path.is_file():
            if kind == "diffuse":
                raise FileNotFoundError(path)
            continue
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(path), check_existing=True)
        node.image.colorspace_settings.name = "sRGB" if kind == "diffuse" else "Non-Color"
        width, height = node.image.size
        limit = 2048 if name == "skin" and tile == 1001 and kind == "diffuse" else 1024
        if max(width, height) > limit:
            ratio = limit / max(width, height)
            node.image.scale(round(width * ratio), round(height * ratio))
            node.image.pack()
        if kind == "normal":
            normal = tree.nodes.new("ShaderNodeNormalMap")
            tree.links.new(node.outputs["Color"], normal.inputs["Color"])
            tree.links.new(normal.outputs["Normal"], shader.inputs[socket])
        else:
            tree.links.new(node.outputs["Color"], shader.inputs[socket])
    return material


def assign_web_materials(directory):
    materials = {name: web_material(directory, name) for name in sorted(set(TEXTURED_MESHES.values()))}
    for object_name, name in TEXTURED_MESHES.items():
        mesh = bpy.data.objects[object_name].data
        mesh.materials.clear()
        mesh.materials.append(materials[name])
    skin = [web_material(directory, "skin", tile) for tile in (1001, 1002, 1003)]
    for name in SKIN_MESHES:
        mesh = bpy.data.objects[name].data
        mesh.materials.clear()
        for material in skin:
            mesh.materials.append(material)
        mesh.uv_layers.active = mesh.uv_layers["UVMap"]
        uv = mesh.uv_layers.active.uv
        for polygon in mesh.polygons:
            tile = math.floor(sum(uv[i].vector.x for i in polygon.loop_indices) / polygon.loop_total)
            if tile not in (0, 1, 2):
                raise RuntimeError(f"Unexpected UDIM tile {tile} for {name}")
            polygon.material_index = tile
            for i in polygon.loop_indices:
                uv[i].vector.x -= tile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--working-copy", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    snow = Path(bpy.data.filepath).resolve()
    working_copy = args.working_copy.resolve()
    if working_copy in (snow, args.source.resolve()):
        raise ValueError("Specify a separate Snow working copy")
    scene = bpy.context.scene
    rig = bpy.data.objects["RIG-Snow"]
    frames, source_rest = source_animation(args.source.resolve(), scene)
    retarget(rig, scene, frames, source_rest)
    rig["asset_credit"] = "Snow Rig (CC) Blender Foundation | studio.blender.org"
    rig["linguistic_review"] = "NOT YET TESTED"
    working_copy.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(working_copy), relative_remap=True, compress=True)
    assign_web_materials(snow.parent / "textures")
    selected = [bpy.data.objects[name] for name in (*SKIN_MESHES, *TEXTURED_MESHES, *DETAIL_MESHES)]
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in [rig, *selected]:
        if obj.name not in bpy.context.view_layer.objects:
            scene.collection.objects.link(obj)
        obj.hide_viewport = False
        obj.hide_set(False)
        obj.select_set(True)
    bpy.data.objects["GEO-snow-pants"].modifiers.new("glTF tangent triangulation", "TRIANGULATE")
    bpy.context.view_layer.objects.active = rig
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    result = bpy.ops.export_scene.gltf(
        filepath=str(output), export_format="GLB", use_selection=True, export_apply=True,
        export_animations=True, export_animation_mode="ACTIVE_ACTIONS",
        export_nla_strips_merged_animation_name=CLIP, export_frame_range=True,
        export_force_sampling=True, export_def_bones=True, export_extras=True,
        export_morph=False, export_morph_animation=False, export_tangents=True,
        export_cameras=False, export_lights=False, export_image_format="JPEG", export_image_quality=83,
    )
    if result != {"FINISHED"} or not output.is_file():
        raise RuntimeError(f"Snow GLB export failed: {result}")


if __name__ == "__main__":
    main()
