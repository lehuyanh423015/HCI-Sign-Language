"""Render front/side review evidence of a sign working file without saving the .blend.

    blender -b blender/working/signs/S004/S004.blend --python blender/scripts/render_sign_review.py -- \
        --output-directory blender/working/signs/S004/previews --frames 1 20 40 60 \
        --contact-sheet S004-key-poses.png --video S004-front-side.mp4

Stills are rendered per view and frame. ``--contact-sheet`` places them in a grid (rows = views),
``--video`` renders the whole clip with the views side by side, H.264 through Blender's own FFmpeg,
so no external tool is needed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

VIEWS = {
    # Camera offsets in the body's local space: the avatar faces -Y.
    "front": (Vector((0.0, -2.1, 1.30)), Vector((0.0, 0.0, 1.22)), 50),
    "side": (Vector((1.75, -0.95, 1.30)), Vector((0.0, -0.1, 1.22)), 50),
    "hands": (Vector((0.0, -1.05, 1.28)), Vector((0.0, -0.15, 1.20)), 55),
    # Close-ups of the upper body, used to review hand shape at chest and face height.
    "upper": (Vector((0.0, -1.15, 1.40)), Vector((0.0, -0.10, 1.33)), 50),
    "upper_side": (Vector((0.85, -0.75, 1.40)), Vector((0.0, -0.12, 1.33)), 50),
    # Tight framing on the hands in front of the chest, from the front and from the avatar's right.
    "hands_front": (Vector((0.0, -0.95, 1.22)), Vector((0.0, -0.22, 1.12)), 60),
    "hands_right": (Vector((-0.75, -0.65, 1.22)), Vector((-0.02, -0.22, 1.12)), 60),
}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--views", nargs="+", default=["front", "side"], choices=sorted(VIEWS))
    parser.add_argument("--every", type=int, default=1)
    parser.add_argument("--frames", type=int, nargs="*")
    parser.add_argument("--resolution", type=int, nargs=2, default=(540, 720))
    parser.add_argument("--focus-bone", help="for still frames, aim at this pose bone; the view offset becomes relative to it")
    parser.add_argument("--focus-distance", type=float, default=0.55)
    parser.add_argument("--contact-sheet", help="file name inside the output directory")
    parser.add_argument("--video", help="file name inside the output directory")
    parser.add_argument("--keep-frames", action="store_true", help="keep individual stills after building the sheet")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    args = arguments()
    scene = bpy.context.scene
    body = bpy.data.objects["Human"]
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.render.resolution_x, scene.render.resolution_y = args.resolution
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = scene.world or bpy.data.worlds.new("REVIEW_WORLD")
    camera = bpy.data.objects.new("SIGN_REVIEW_CAMERA", bpy.data.cameras.new("SIGN_REVIEW_CAMERA"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    out = Path(args.output_directory).resolve()
    out.mkdir(parents=True, exist_ok=True)
    frames = args.frames or list(range(scene.frame_start, scene.frame_end + 1, max(1, args.every)))
    written = []
    for view in args.views:
        offset, target, lens = VIEWS[view]
        camera.location = body.matrix_world @ offset
        camera.data.lens = lens
        look_at(camera, body.matrix_world @ target)
        for frame in frames:
            scene.frame_set(frame)
            if args.focus_bone:
                # Keep the camera direction of the view but frame the chosen bone at a fixed distance.
                armature = bpy.data.objects["Human.rig"]
                bone_point = armature.matrix_world @ armature.pose.bones[args.focus_bone].head
                view_dir = (body.matrix_world @ offset - body.matrix_world @ target).normalized()
                camera.location = bone_point + view_dir * args.focus_distance
                look_at(camera, bone_point)
            path = out / f"{view}-{frame:04d}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            written.append(path.name)
    summary = {"scene": Path(bpy.data.filepath).name, "frames": frames, "views": args.views, "stills": written}
    if args.contact_sheet:
        summary["contact_sheet"] = contact_sheet(out, args.views, frames, out / args.contact_sheet)
        if not args.keep_frames:
            for name in written:
                (out / name).unlink()
            summary["stills"] = []
    if args.video:
        summary["video"] = render_video(scene, camera, body, args.views, out / args.video, args.resolution)
    (out / "review.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"PASS rendered review evidence -> {out}")


def load_pixels(path):
    image = bpy.data.images.load(str(path))
    w, h = image.size
    pixels = np.empty(w * h * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image)
    return pixels.reshape(h, w, 4)


def save_pixels(pixels, path):
    h, w = pixels.shape[:2]
    image = bpy.data.images.new(path.stem, width=w, height=h, alpha=True)
    image.pixels.foreach_set(np.ascontiguousarray(pixels, dtype=np.float32).ravel())
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def contact_sheet(out, views, frames, path):
    # Blender image rows start at the bottom, so the first view is stacked last to appear on top.
    rows = [np.concatenate([load_pixels(out / f"{view}-{frame:04d}.png") for frame in frames], axis=1) for view in views]
    save_pixels(np.concatenate(rows[::-1], axis=0), path)
    return path.name


def render_video(scene, camera, body, views, path, resolution):
    """Render each view as a PNG sequence, join them side by side, then encode with Blender's sequencer."""
    tmp = path.parent / f"_{path.stem}_frames"
    tmp.mkdir(exist_ok=True)
    for view in views:
        offset, target, lens = VIEWS[view]
        camera.location = body.matrix_world @ offset
        camera.data.lens = lens
        look_at(camera, body.matrix_world @ target)
        for frame in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(frame)
            scene.render.filepath = str(tmp / f"{view}-{frame:04d}.png")
            bpy.ops.render.render(write_still=True)
    joined = []
    for frame in range(scene.frame_start, scene.frame_end + 1):
        name = tmp / f"joined-{frame:04d}.png"
        save_pixels(np.concatenate([load_pixels(tmp / f"{view}-{frame:04d}.png") for view in views], axis=1), name)
        joined.append(name)
    video_scene = bpy.data.scenes.new("SIGN_REVIEW_VIDEO")
    video_scene.render.fps = scene.render.fps
    video_scene.render.resolution_x = resolution[0] * len(views)
    video_scene.render.resolution_y = resolution[1]
    video_scene.render.resolution_percentage = 100
    video_scene.frame_start, video_scene.frame_end = 1, len(joined)
    editor = video_scene.sequence_editor_create()
    strips = editor.strips if hasattr(editor, "strips") else editor.sequences
    strip = strips.new_image("frames", str(joined[0]), 1, 1)
    for name in joined[1:]:
        strip.elements.append(name.name)
    settings = video_scene.render.image_settings
    if hasattr(settings, "media_type"):
        settings.media_type = "VIDEO"
    settings.file_format = "FFMPEG"
    video_scene.render.ffmpeg.format = "MPEG4"
    video_scene.render.ffmpeg.codec = "H264"
    video_scene.render.ffmpeg.constant_rate_factor = "HIGH"
    video_scene.render.use_sequencer = True
    video_scene.render.filepath = str(path)
    bpy.ops.render.render(animation=True, scene=video_scene.name)
    for item in tmp.iterdir():
        item.unlink()
    tmp.rmdir()
    if not path.exists():
        produced = next(iter(sorted(path.parent.glob(f"{path.stem}*.mp4"))), None)
        if produced:
            produced.rename(path)
    return {"file": path.name, "frames": len(joined), "fps": scene.render.fps, "exists": path.exists()}


if __name__ == "__main__":
    main()
