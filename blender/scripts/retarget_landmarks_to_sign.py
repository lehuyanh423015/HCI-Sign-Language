"""Author a draft ``Snnn_MAIN`` Action from MediaPipe Holistic landmarks.

Run with Blender 5.2.4 on a working copy created by ``create_sign_working_copy.py``::

    blender -b blender/working/signs/S004/S004_base.blend --python blender/scripts/retarget_landmarks_to_sign.py -- \
        --raw S004.raw.json --sign-id S004 --start 0.2 --end 2.1 \
        --output-blend blender/working/signs/S004/S004.blend --report blender/working/signs/S004/evidence/retarget.json

Input is a ``vsl-raw-landmarks`` v1 file (MediaPipe Holistic per frame, 30 FPS sampling). The script
solves rotations geometrically in the armature's own space: for every bone segment it rotates the
rest direction measured on Master Avatar v1 onto the direction seen in the landmarks. It never edits
rest pose, hierarchy, bindings or Morph Targets; it only creates one Action with an OBJECT slot.

The result is a technical draft that still needs animator cleanup, visual review and linguistic review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from master_v1_utils import inventory, neutral_state, write_json

MASTER_SHA256 = "DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC"

# MediaPipe Pose indices; "L" is the signer's own left side.
POSE = {"L": (11, 13, 15), "R": (12, 14, 16)}
# Hand landmark chains per MPFB finger: finger1 = thumb ... finger5 = little finger.
FINGERS = {1: (1, 2, 3, 4), 2: (5, 6, 7, 8), 3: (9, 10, 11, 12), 4: (13, 14, 15, 16), 5: (17, 18, 19, 20)}
FACE = {"eye_outer_r": 33, "eye_outer_l": 263, "forehead": 10, "chin": 152}

# Hand-shape overrides for the four fingers (index to little). MediaPipe often under-estimates finger
# flexion when fingers are occluded, so the animator can impose a shape on a time range while palm
# orientation and the thumb still follow the video. Angles are flexion in degrees at MCP, PIP, DIP;
# ``spread`` pulls the fingers parallel to the middle finger (0 keeps the rig's natural spread).
# These are technical building blocks, not a validated VSL handshape inventory.
HANDSHAPES = {
    "fist": {"flex": (95, 105, 70), "spread": 0.7},
    "flat": {"flex": (4, 4, 2), "spread": 0.3},
    "bunched": {"flex": (48, 38, 22), "spread": 1.0},
}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="vsl-raw-landmarks JSON")
    parser.add_argument("--sign-id", required=True)
    parser.add_argument("--clip")
    parser.add_argument("--start", type=float, default=0.0, help="segment start, seconds")
    parser.add_argument("--end", type=float, default=1e9, help="segment end, seconds")
    parser.add_argument("--lead-in", type=int, default=8, help="frames blending from neutral")
    parser.add_argument("--lead-out", type=int, default=12, help="frames blending back to neutral")
    parser.add_argument("--direct-return", action="store_true",
                        help="blend straight from the last pose to neutral instead of passing through the segment's first pose")
    parser.add_argument("--handshape", action="append", default=[],
                        help="SIDE:SHAPE[:START:END] with SIDE L or R, SHAPE in " + ", ".join(HANDSHAPES)
                        + "; times in source seconds, default the whole segment")
    parser.add_argument("--smooth", type=int, default=2, help="triangular window radius in frames")
    parser.add_argument("--head-weight", type=float, default=0.7)
    parser.add_argument("--hand-depth-scale", type=float, default=1.0,
                        help="scale for hand landmark depth; lower it when the hand points toward the camera in 3D but not in the image")
    parser.add_argument("--arm-mode", choices=("ik", "direction"), default="ik",
                        help="ik keeps wrist position relative to the shoulder; direction copies segment directions")
    parser.add_argument("--depth-scale", type=float, default=0.5,
                        help="scale for body landmark depth; MediaPipe tends to exaggerate how far the arms reach forward")
    parser.add_argument("--no-head", action="store_true")
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


# ---------- geometry ----------

def to_rig(point, sx=1.0, sy=1.0, depth=1.0):
    """MediaPipe (x right of image, y down, z toward camera negative) to armature space.

    The signer faces the camera and the avatar faces -Y, so image right is avatar +X (its left),
    up is +Z, and a smaller MediaPipe z (closer to the camera) is -Y.
    """
    return Vector((point["x"] * sx, point["z"] * sx * depth, -point["y"] * sy))


def direction(a, b):
    v = b - a
    return v.normalized() if v.length > 1e-9 else None


def basis(primary, secondary):
    x = primary.normalized()
    y = secondary - x * secondary.dot(x)
    if y.length < 1e-6:
        return None
    y.normalize()
    return Matrix((x, y, x.cross(y))).transposed()


def from_basis(rest_a, rest_b, target_a, target_b):
    """Rotation mapping (rest_a, rest_b) onto (target_a, target_b); a is primary, b is orthogonalised."""
    m1, m2 = basis(rest_a, rest_b), basis(target_a, target_b)
    if m1 is None or m2 is None:
        return rest_a.rotation_difference(target_a).to_matrix()
    return m2 @ m1.transposed()


def unit_from(a, b):
    return a.rotation_difference(b).to_matrix()


# ---------- solver ----------

class Solver:
    def __init__(self, armature, depth_scale=1.0, arm_mode="ik", hand_depth=1.0):
        self.depth = depth_scale
        self.hand_depth = hand_depth
        self.arm_mode = arm_mode
        self.arm_scale = {"L": 1.0, "R": 1.0}
        self.bones = armature.data.bones
        self.rest = {b.name: b.matrix_local.to_3x3().normalized() for b in self.bones}
        self.head = {b.name: b.head_local.copy() for b in self.bones}
        # Mouth centre between the lip-corner bones; used as an anchor for signs made at the mouth.
        self.mouth = (self.head["oris03.L"] + self.head["oris03.R"]) * 0.5
        self.face_weights = []
        self.contact_frames = 0
        self.handshapes = []
        self.segment_bounds = (0.0, 0.0)
        self.prev_bend = {}

    def identity_matrix(self, name, parent_matrix):
        """Armature-space orientation of ``name`` when its own pose basis is identity."""
        parent = self.bones[name].parent
        if parent is None:
            return self.rest[name].copy()
        return parent_matrix @ self.rest[parent.name].inverted() @ self.rest[name]

    def local(self, name, parent_matrix, desired):
        """Pose basis rotation that gives ``desired`` armature-space orientation."""
        return (self.identity_matrix(name, parent_matrix).inverted() @ desired).to_quaternion()

    def segment(self, a, b):
        return (self.head[b] - self.head[a]).normalized()

    def calibrate(self, frames):
        """Ratio between avatar arm length and the signer's median arm length, per side."""
        for side in ("L", "R"):
            i_sh, i_el, i_wr = POSE[side]
            lengths = []
            for f in frames:
                pose = f.get("pose3d") or []
                if len(pose) >= 17:
                    p = [to_rig(pose[i], depth=self.depth) for i in (i_sh, i_el, i_wr)]
                    lengths.append((p[1] - p[0]).length + (p[2] - p[1]).length)
            s = side
            avatar = (self.head[f"lowerarm01.{s}"] - self.head[f"upperarm01.{s}"]).length + (self.head[f"wrist.{s}"] - self.head[f"lowerarm01.{s}"]).length
            if lengths:
                self.arm_scale[side] = avatar / sorted(lengths)[len(lengths) // 2]
        return dict(self.arm_scale)

    def two_bone_ik(self, side, p_sh, p_el, p_wr, pose=None, contact=None):
        """Keep the wrist POSITION relative to the shoulder, scaled to the avatar's arm length.

        Location is a meaningful sign parameter, so the wrist target matters more than the exact
        segment directions. The elbow stays on the same side of the shoulder-wrist line as in the video.
        """
        s = side
        a = (self.head[f"lowerarm01.{s}"] - self.head[f"upperarm01.{s}"]).length
        b = (self.head[f"wrist.{s}"] - self.head[f"lowerarm01.{s}"]).length
        shoulder = self.head[f"upperarm01.{s}"]
        target = shoulder + (p_wr - p_sh) * self.arm_scale[side]
        if pose is not None and len(pose) > 10:
            # Near the face, place the wrist relative to the mouth instead of the shoulder: the shoulder
            # landmark sits on top of the shoulder while the rig joint is lower, and the avatar's neck differs.
            mouth = (to_rig(pose[9], depth=self.depth) + to_rig(pose[10], depth=self.depth)) * 0.5
            distance = (p_wr - mouth).length
            weight = min(1.0, max(0.0, (0.35 - distance) / 0.15))
            weight = weight * weight * (3 - 2 * weight)
            if weight > 0:
                face_target = self.mouth + (p_wr - mouth) * self.arm_scale[side]
                target = target.lerp(face_target, weight)
            self.face_weights.append(weight)
        if contact is not None and contact[0] > 0:
            # The image shows the fingertips at the mouth: place the wrist so the avatar's fingertips touch
            # its lips. 3D landmark depth is unreliable here, the 2D contact is not.
            lip = self.mouth + Vector((0.0, -0.012, 0.0))
            target = target.lerp(lip - contact[1], contact[0])
        u = target - shoulder
        d = u.length
        if d < 1e-6:
            return None
        u /= d
        d = min(max(d, abs(a - b) + 1e-4), a + b - 1e-4)
        pole = (p_el - p_sh)
        pole = pole - u * pole.dot(u)
        if pole.length < 1e-4:
            return None
        pole.normalize()
        cos_a = (a * a + d * d - b * b) / (2 * a * d)
        sin_a = math.sqrt(max(0.0, 1.0 - cos_a * cos_a))
        elbow = shoulder + (u * cos_a + pole * sin_a) * a
        wrist = shoulder + u * d
        return (elbow - shoulder).normalized(), (wrist - elbow).normalized()

    def handshape_weight(self, side, t):
        """Which override applies to this side at source time t, with a short ease at inner boundaries."""
        ramp = 0.12
        seg_a, seg_b = self.segment_bounds
        for hs_side, name, a, b in self.handshapes:
            if hs_side != side or not (a - ramp <= t <= b + ramp):
                continue
            left = 1.0 if a <= seg_a + 1e-6 else min(1.0, max(0.0, (t - a + ramp) / ramp))
            right = 1.0 if b >= seg_b - 1e-6 else min(1.0, max(0.0, (b + ramp - t) / ramp))
            weight = min(left, right)
            return HANDSHAPES[name], weight * weight * (3 - 2 * weight)
        return None, 0.0

    def shaped_directions(self, side, finger, palm_rotation, shape):
        """Segment directions of one finger for a hand-shape preset, in armature space."""
        s = side
        rest_forward = (self.head[f"finger3-1.{s}"] - self.head[f"wrist.{s}"]).normalized()
        rest_across = (self.head[f"finger2-1.{s}"] - self.head[f"finger5-1.{s}"]).normalized()
        # Palm side of the hand: the cross product points to the back of the right hand and the palm of the left.
        normal = rest_forward.cross(rest_across).normalized() * (1.0 if side == "L" else -1.0)

        def flat_direction(n):
            d = self.head[f"finger{n}-2.{s}"] - self.head[f"finger{n}-1.{s}"]
            d = d - normal * d.dot(normal)
            return d.normalized()

        base = flat_direction(finger).lerp(flat_direction(3), shape["spread"]).normalized()
        base = palm_rotation @ base
        palm_normal = (palm_rotation @ normal).normalized()
        axis = base.cross(palm_normal)
        if axis.length < 1e-6:
            return None
        axis.normalize()
        out, total = [], 0.0
        for angle in shape["flex"]:
            total += math.radians(angle)
            out.append((Matrix.Rotation(total, 3, axis) @ base).normalized())
        return out

    def mouth_contact(self, side, frame, hp, width, height):
        """Weight 0..1 that the fingertips touch the mouth in the image, and the avatar wrist-to-fingertip vector."""
        pose2d = frame.get("pose2d") or []
        image = frame.get(f"{'left' if side == 'L' else 'right'}Hand") or []
        if hp is None or len(pose2d) < 13 or len(image) != 21:
            return None
        px = lambda p: Vector((p["x"] * width, p["y"] * height))
        mouth = (px(pose2d[9]) + px(pose2d[10])) * 0.5
        shoulders = (px(pose2d[11]) - px(pose2d[12])).length
        tips = (px(image[4]) + px(image[8]) + px(image[12])) / 3
        if shoulders < 1:
            return None
        t = min(1.0, max(0.0, (0.35 - (tips - mouth).length / shoulders) / 0.20))
        weight = t * t * (3 - 2 * t)
        tip_mean = (hp[4] + hp[8] + hp[12]) / 3
        palm = (hp[9] - hp[0]).length
        if palm < 1e-6:
            return None
        ratio = (self.head[f"finger3-1.{side}"] - self.head[f"wrist.{side}"]).length / palm
        if weight > 0.5:
            self.contact_frames += 1
        return weight, (tip_mean - hp[0]) * ratio

    def solve_frame(self, frame, width, height, use_head, head_weight):
        out = {}
        pose = frame.get("pose3d") or []
        for side in ("L", "R"):
            s = side
            u1, u2, l1, l2, w = (f"upperarm01.{s}", f"upperarm02.{s}", f"lowerarm01.{s}", f"lowerarm02.{s}", f"wrist.{s}")
            # Parents of the arm chain stay at rest, so the shoulder frame is its rest orientation.
            m_shoulder = self.rest[f"shoulder01.{s}"]
            m_l2 = None
            hand_world = frame.get(f"{'left' if side == 'L' else 'right'}HandWorld") or []
            hand_image = frame.get(f"{'left' if side == 'L' else 'right'}Hand") or []
            if len(hand_world) == 21:
                hp = [to_rig(p, depth=self.hand_depth) for p in hand_world]
            elif len(hand_image) == 21:
                hp = [to_rig(p, width, height, depth=self.hand_depth) for p in hand_image]
            else:
                hp = None
            contact = self.mouth_contact(side, frame, hp, width, height)
            if len(pose) >= 17:
                i_sh, i_el, i_wr = POSE[side]
                p_sh, p_el, p_wr = (to_rig(pose[i], depth=self.depth) for i in (i_sh, i_el, i_wr))
                d_upper, d_lower = direction(p_sh, p_el), direction(p_el, p_wr)
                if d_upper and d_lower:
                    rest_upper = self.segment(u1, l1)
                    rest_lower = self.segment(l1, w)
                    rest_bend = rest_lower - rest_upper * rest_lower.dot(rest_upper)
                    if self.arm_mode == "ik":
                        d_upper, d_lower = self.two_bone_ik(side, p_sh, p_el, p_wr, pose, contact) or (d_upper, d_lower)
                    bend = d_lower - d_upper * d_lower.dot(d_upper)
                    if bend.length < 0.15:
                        bend = self.prev_bend.get(side, rest_bend.copy())
                    bend = bend.normalized()
                    self.prev_bend[side] = bend.copy()
                    r_upper = from_basis(rest_upper, rest_bend, d_upper, bend)
                    m_u1 = r_upper @ self.identity_matrix(u1, m_shoulder)
                    out[u1] = self.local(u1, m_shoulder, m_u1)
                    m_u2 = self.identity_matrix(u2, m_u1)
                    m_l1_id = self.identity_matrix(l1, m_u2)
                    r_lower = unit_from(r_upper @ rest_lower, d_lower)
                    m_l1 = r_lower @ m_l1_id
                    out[l1] = self.local(l1, m_u2, m_l1)
                    m_l2 = self.identity_matrix(l2, m_l1)

            if hp is None or m_l2 is None:
                continue

            # Palm frame: wrist to middle-finger base, and little-finger base to index base.
            rest_forward = (self.head[f"finger3-1.{s}"] - self.head[w]).normalized()
            rest_across = (self.head[f"finger2-1.{s}"] - self.head[f"finger5-1.{s}"]).normalized()
            t_forward, t_across = direction(hp[0], hp[9]), direction(hp[17], hp[5])
            if not t_forward or not t_across:
                continue
            palm_rotation = from_basis(rest_forward, rest_across, t_forward, t_across)
            m_w = palm_rotation @ self.rest[w]
            # Share forearm twist: half on lowerarm02, the rest on the wrist, to limit candy-wrapper skinning.
            m_w_id = self.identity_matrix(w, m_l2)
            delta = (m_l2.inverted() @ m_w) @ (m_l2.inverted() @ m_w_id).inverted()
            dq = delta.to_quaternion()
            twist = Quaternion((dq.w, 0.0, dq.y, 0.0))
            if twist.magnitude > 1e-9:
                twist.normalize()
                half = Quaternion().slerp(twist, 0.5)
                out[l2] = half
                m_l2 = self.identity_matrix(l2, m_l1) @ half.to_matrix()
            out[w] = self.local(w, m_l2, m_w)

            shape, shape_weight = self.handshape_weight(side, frame["t"])
            for finger, idx in FINGERS.items():
                chain = [f"finger{finger}-{k}.{s}" for k in (1, 2, 3)]
                shaped = self.shaped_directions(side, finger, palm_rotation, shape) if shape and finger != 1 and shape_weight > 0 else None
                first_parent = w if finger == 1 else f"metacarpal{finger - 1}.{s}"
                parent_matrix = m_w if finger == 1 else self.identity_matrix(first_parent, m_w)
                for k, bone in enumerate(chain):
                    target = direction(hp[idx[k]], hp[idx[k + 1]])
                    if shaped:
                        target = shaped[k] if target is None else target.lerp(shaped[k], shape_weight).normalized()
                    m_id = self.identity_matrix(bone, parent_matrix)
                    if target is None:
                        out[bone] = Quaternion()
                        parent_matrix = m_id
                        continue
                    m_b = unit_from(m_id.col[1].to_3d().normalized(), target) @ m_id
                    out[bone] = self.local(bone, parent_matrix, m_b)
                    parent_matrix = m_b

        face = frame.get("face") or []
        if use_head and len(face) > FACE["chin"]:
            q = lambda i: to_rig(face[i], width, height)
            across = direction(q(FACE["eye_outer_r"]), q(FACE["eye_outer_l"]))
            up = direction(q(FACE["chin"]), q(FACE["forehead"]))
            if across and up:
                r = from_basis(Vector((1, 0, 0)), Vector((0, 0, 1)), across, up).to_quaternion()
                r = Quaternion().slerp(r, head_weight)
                # Neck chain stays at rest; apply the head turn as an armature-space delta on ``head``.
                m_parent = self.identity_matrix("neck03", self.identity_matrix("neck02", self.identity_matrix("neck01", self.rest["spine01"])))
                m_head = r.to_matrix() @ self.identity_matrix("head", m_parent)
                out["head"] = self.local("head", m_parent, m_head)
        return out


# ---------- tracks ----------

def fill_track(track):
    known = [i for i, q in enumerate(track) if q is not None]
    if not known:
        return track
    out = list(track)
    for i in range(known[0]):
        out[i] = track[known[0]].copy()
    for a, b in zip(known, known[1:]):
        for i in range(a + 1, b):
            out[i] = track[a].slerp(track[b], (i - a) / (b - a))
    for i in range(known[-1] + 1, len(track)):
        out[i] = track[known[-1]].copy()
    return out


def align(track):
    for i in range(1, len(track)):
        if track[i].dot(track[i - 1]) < 0:
            track[i] = -track[i]
    return track


def smooth(track, radius):
    if radius <= 0:
        return track
    out = []
    for i in range(len(track)):
        acc, total = [0.0] * 4, 0.0
        for j in range(max(0, i - radius), min(len(track), i + radius + 1)):
            weight = radius + 1 - abs(i - j)
            q = track[j]
            acc = [acc[0] + q.w * weight, acc[1] + q.x * weight, acc[2] + q.y * weight, acc[3] + q.z * weight]
            total += weight
        out.append(Quaternion([v / total for v in acc]).normalized())
    return out


def ease(t):
    return t * t * (3 - 2 * t)


# ---------- main ----------

def main():
    args = arguments()
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError(f"Expected Blender {args.expected_version}, got {bpy.app.version_string}")
    scene = bpy.context.scene
    sign_id = args.sign_id.upper()
    clip = args.clip or f"{sign_id}_MAIN"
    if scene.get("sign_id") != sign_id or scene.get("source_master_sha256") != MASTER_SHA256:
        raise RuntimeError("Input is not a Master Avatar v1 working copy for this sign")
    output = Path(args.output_blend).resolve()
    if output.exists() or output == Path(bpy.data.filepath).resolve():
        raise RuntimeError(f"Refusing to overwrite: {output}")
    if bpy.data.actions.get(clip):
        raise RuntimeError(f"Action already exists: {clip}")
    armature = bpy.data.objects.get("Human.rig")
    if armature is None:
        raise RuntimeError("Human.rig missing")
    before = inventory()

    raw_path = Path(args.raw).resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("format") != "vsl-raw-landmarks":
        raise RuntimeError("Unsupported landmark file")
    frames = [f for f in raw["frames"] if args.start - 1e-6 <= f["t"] <= args.end + 1e-6]
    if len(frames) < 2:
        raise RuntimeError("Segment has fewer than 2 frames")
    if abs(raw["fps"] - scene.render.fps) > 1e-6:
        raise RuntimeError(f"Landmarks sampled at {raw['fps']} FPS, scene is {scene.render.fps}")

    solver = Solver(armature, args.depth_scale, args.arm_mode, args.hand_depth_scale)
    arm_scale = solver.calibrate(frames)
    solver.segment_bounds = (frames[0]["t"], frames[-1]["t"])
    for spec in args.handshape:
        parts = spec.split(":")
        if len(parts) not in (2, 4) or parts[0] not in ("L", "R") or parts[1] not in HANDSHAPES:
            raise RuntimeError(f"Invalid --handshape {spec}")
        a, b = (float(parts[2]), float(parts[3])) if len(parts) == 4 else solver.segment_bounds
        solver.handshapes.append((parts[0], parts[1], a, b))
    solved = [solver.solve_frame(f, raw["width"], raw["height"], not args.no_head, args.head_weight) for f in frames]
    names = sorted({name for row in solved for name in row})
    tracks = {}
    coverage = {}
    for name in names:
        track = [row.get(name) for row in solved]
        coverage[name] = round(sum(q is not None for q in track) / len(track), 3)
        tracks[name] = smooth(align(fill_track(track)), args.smooth)

    # Timeline: frame 1 neutral, ease into the first solved pose, play the segment, ease back to neutral.
    n = len(frames)
    start = 1 + args.lead_in
    last = start + n - 1 + args.lead_out
    identity = Quaternion()
    action = bpy.data.actions.new(clip)
    armature.animation_data_create()
    armature.animation_data.action = action
    keyed = 0
    for name, track in tracks.items():
        values = {1: identity}
        for k in range(1, args.lead_in):
            values[1 + k] = identity.slerp(track[0], ease(k / args.lead_in))
        for i, q in enumerate(track):
            values[start + i] = q
        half = 0 if args.direct_return else args.lead_out // 2
        for k in range(1, args.lead_out):
            if k <= half:
                # Lower the hands back to the signer's own resting pose first, so the hand does not sweep across the face.
                values[start + n - 1 + k] = track[-1].slerp(track[0], ease(k / half))
            else:
                values[start + n - 1 + k] = (track[0] if half else track[-1]).slerp(identity, ease((k - half) / (args.lead_out - half)))
        values[last] = identity
        series = align([values[f] for f in sorted(values)])
        frames_sorted = sorted(values)
        data_path = f'pose.bones["{name}"].rotation_quaternion'
        for component in range(4):
            fcurve = action.fcurve_ensure_for_datablock(armature, data_path, index=component, group_name=name)
            fcurve.keyframe_points.add(len(frames_sorted))
            co = []
            for f, q in zip(frames_sorted, series):
                co.extend((float(f), float(q[component])))
            fcurve.keyframe_points.foreach_set("co", co)
            for point in fcurve.keyframe_points:
                point.interpolation = "LINEAR"
            fcurve.update()
            keyed += len(frames_sorted)

    scene.frame_start = 1
    scene.frame_end = last
    scene["sign_pipeline_status"] = "IN_PRODUCTION"
    scene["animation_method"] = "MEDIAPIPE_HOLISTIC_GEOMETRIC_RETARGET_DRAFT"
    scene["animation_source_landmarks_sha256"] = sha256_file(raw_path)
    scene["animation_source_media"] = raw.get("source")
    scene["animation_source_segment_seconds"] = [args.start, args.end]
    scene.frame_set(1)
    bpy.context.view_layer.update()
    neutral = neutral_state()
    after = inventory()
    # Only the new clip may differ; rig, bindings, geometry, transforms and Morph Targets must stay identical.
    rig_unchanged = {k: v for k, v in before.items() if k != "actions"} == {k: v for k, v in after.items() if k != "actions"}
    if not rig_unchanged or sorted(after["actions"]) != sorted(before["actions"] + [clip]):
        raise RuntimeError("Retarget changed the rig inventory")
    if neutral["pose_non_identity"]:
        raise RuntimeError(f"Frame 1 is not neutral: {neutral['pose_non_identity'][:5]}")

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    write_json(args.report, {
        "schema_version": 1,
        "artifact": "sign_landmark_retarget",
        "status": "PASS",
        "classification": "SIGN_PRODUCTION_CANDIDATE",
        "linguistic_status": "NOT YET TESTED",
        "method": scene["animation_method"],
        "blender_version": bpy.app.version_string,
        "sign_id": sign_id,
        "clip": clip,
        "landmarks": {"path": raw_path.name, "sha256": scene["animation_source_landmarks_sha256"], "source_media": raw.get("source"), "fps": raw["fps"]},
        "segment_seconds": [args.start, args.end],
        "segment_frames": n,
        "return_via_first_pose": not args.direct_return,
        "timeline": {"frame_start": 1, "motion_start": start, "motion_end": start + n - 1, "frame_end": last, "lead_in": args.lead_in, "lead_out": args.lead_out},
        "smoothing_radius": args.smooth,
        "depth_scale": args.depth_scale,
        "arm_mode": args.arm_mode,
        "hand_depth_scale": args.hand_depth_scale,
        "handshape_overrides": [{"side": h[0], "shape": h[1], "seconds": [h[2], h[3]], "flex_degrees": HANDSHAPES[h[1]]["flex"], "spread": HANDSHAPES[h[1]]["spread"]} for h in solver.handshapes],
        "frames_with_mouth_anchor": sum(1 for w in solver.face_weights if w > 0.5),
        "frames_with_mouth_contact": solver.contact_frames,
        "arm_scale": arm_scale,
        "head_weight": 0.0 if args.no_head else args.head_weight,
        "animated_bones": len(tracks),
        "keyframes_written": keyed,
        "solved_coverage": coverage,
        "rig_inventory_unchanged": rig_unchanged,
        "neutral_frame_1": not neutral["pose_non_identity"],
        "output": {"path": str(output), "sha256": sha256_file(output)},
    })
    print(f"PASS landmark retarget: {clip} frames 1-{last}, {len(tracks)} bones -> {output}")


if __name__ == "__main__":
    main()
