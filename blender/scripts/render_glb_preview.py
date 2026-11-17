"""Import a GLB into a clean Blender scene and render visual evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--frame", type=int, default=1)
    parser.add_argument("--disable-skin", action="store_true")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    args = arguments()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(Path(args.input).resolve()))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("Imported GLB has no mesh objects")
    helper = bpy.data.objects.get("Icosphere")
    if helper:
        helper.hide_render = True
    if args.disable_skin:
        for obj in meshes:
            for modifier in obj.modifiers:
                if modifier.type == "ARMATURE":
                    modifier.show_render = False
                    modifier.show_viewport = False

    world_points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    minimum = Vector(tuple(min(point[index] for point in world_points) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in world_points) for index in range(3)))
    center = (minimum + maximum) * 0.5
    size = maximum - minimum

    camera_data = bpy.data.cameras.new("GLB_PREVIEW_CAMERA_DATA")
    camera = bpy.data.objects.new("GLB_PREVIEW_CAMERA", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = center + Vector((0.0, -max(size.z * 1.85, 2.2), size.z * 0.02))
    camera_data.lens = 58
    camera_data.clip_start = 0.01
    look_at(camera, center)
    bpy.context.scene.camera = camera

    for name, energy, location in (
        ("KEY", 900, center + Vector((-1.8, -2.0, 2.4))),
        ("FILL", 450, center + Vector((1.8, -1.0, 1.4))),
        ("RIM", 600, center + Vector((0.0, 1.5, 2.0))),
    ):
        data = bpy.data.lights.new("GLB_%s_DATA" % name, "AREA")
        data.energy = energy
        data.size = 2.0
        light = bpy.data.objects.new("GLB_%s" % name, data)
        bpy.context.scene.collection.objects.link(light)
        light.location = location
        look_at(light, center)

    scene = bpy.context.scene
    scene.frame_set(args.frame)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("GLB_PREVIEW_WORLD")
    scene.world.color = (0.025, 0.035, 0.033)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    print("PASS imported GLB preview: %s" % output)


if __name__ == "__main__":
    main()
