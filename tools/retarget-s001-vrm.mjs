import { readFileSync, writeFileSync } from 'node:fs';
import { AnimationClip, AnimationMixer, InterpolateDiscrete, InterpolateLinear, LoopOnce, Matrix4, Object3D, Quaternion, Vector3 } from 'three';

const [snowPath, vrmPath, outputPath] = process.argv.slice(2);
if (!snowPath || !vrmPath || !outputPath || outputPath === vrmPath || outputPath === snowPath) {
  throw new Error('Usage: node tools/retarget-s001-vrm.mjs snow.glb avatar.vrm output.glb');
}

function readGlb(path) {
  const bytes = readFileSync(path);
  if (bytes.readUInt32LE(0) !== 0x46546c67 || bytes.readUInt32LE(4) !== 2) {
    throw new Error('Expected glTF 2 GLB');
  }
  const end = 20 + bytes.readUInt32LE(12);
  const doc = JSON.parse(bytes.subarray(20, end));
  return { doc, bin: bytes.subarray(end + 8) };
}

function skeleton(doc) {
  const root = new Object3D();
  const nodes = doc.nodes.map((entry) => {
    const node = new Object3D();
    node.name = entry.name;
    if (entry.matrix) {
      new Matrix4().fromArray(entry.matrix).decompose(node.position, node.quaternion, node.scale);
    } else {
      if (entry.translation) node.position.fromArray(entry.translation);
      if (entry.rotation) node.quaternion.fromArray(entry.rotation);
      if (entry.scale) node.scale.fromArray(entry.scale);
    }
    return node;
  });
  doc.nodes.forEach((entry, index) => (entry.children ?? []).forEach((child) => nodes[index].add(nodes[child])));
  nodes.filter((node) => !node.parent).forEach((node) => root.add(node));
  return { root, nodes };
}

const source = readGlb(snowPath);
const target = readGlb(vrmPath);
const snow = skeleton(source.doc);
const vrm = skeleton(target.doc);
const clip = source.doc.animations.find((animation) => animation.name === 'S001_MAIN');
const humanoid = new Map(target.doc.extensions.VRM.humanoid.humanBones.map(({ bone, node }) => [bone, node]));
const sourceNodes = new Map(snow.nodes.map((node) => [node.name, node]));
const tracks = clip.channels.map(({ sampler, target: channel }) => {
  const { input, output, interpolation = 'LINEAR' } = clip.samplers[sampler];
  if (!['LINEAR', 'STEP'].includes(interpolation)) throw new Error('Expected baked Snow animation');
  const property = channel.path === 'translation' ? 'position' : channel.path === 'rotation' ? 'quaternion' : 'scale';
  const read = (index, size) => {
    const accessor = source.doc.accessors[index];
    const view = source.doc.bufferViews[accessor.bufferView];
    if (accessor.componentType !== 5126 || view.byteStride) throw new Error('Expected packed floats');
    const start = (view.byteOffset ?? 0) + (accessor.byteOffset ?? 0);
    return Float32Array.from({ length: accessor.count * size }, (_, i) => source.bin.readFloatLE(start + 4 * i));
  };
  const Type = property === 'quaternion' ? 'quaternion' : 'vector';
  return { name: `${snow.nodes[channel.node].uuid}.${property}`, type: Type, times: read(input, 1),
    values: read(output, Type === 'quaternion' ? 4 : 3),
    interpolation: interpolation === 'STEP' ? InterpolateDiscrete : InterpolateLinear };
});

const animation = AnimationClip.parse({ name: clip.name, duration: -1, tracks });
const position = (bone) => bone.getWorldPosition(new Vector3());
const rotation = (bone) => bone.getWorldQuaternion(new Quaternion());
function palm([wrist, index, little]) {
  const a = position(index);
  const b = position(little);
  const across = a.clone().sub(b).normalize();
  const normal = new Vector3().crossVectors(across, a.add(b).multiplyScalar(0.5).sub(position(wrist))).normalize();
  const forward = new Vector3().crossVectors(normal, across);
  return new Quaternion().setFromRotationMatrix(new Matrix4().makeBasis(across, forward, normal));
}

// VRM 0 faces -Z and Snow faces +Z.
snow.root.rotateY(Math.PI);
const outputTracks = new Map();
const mappings = ['L', 'R'].map((side) => {
  const prefix = side === 'L' ? 'left' : 'right';
  const from = (name) => sourceNodes.get(`DEF-${name}.${side}`);
  const to = (name) => vrm.nodes[humanoid.get(prefix + name)];
  const sourceArm = ['UpperArm_1', 'Forearm_1', 'Wrist'].map(from);
  const targetArm = ['UpperArm', 'LowerArm', 'Hand'].map(to);
  const sourcePalm = [from('Wrist'), from('Finger_Index1'), from('Finger_Pinky1')];
  const targetPalm = [to('Hand'), to('IndexProximal'), to('LittleProximal')];
  const sourceNeutral = palm(sourcePalm);
  const targetNeutral = palm(targetPalm);
  const fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Little'].flatMap((finger) =>
    ['Proximal', 'Intermediate', 'Distal'].map((joint, index) => {
      const src = from(`Finger_${finger === 'Little' ? 'Pinky' : finger}${index + 1}`);
      const dst = to(finger + joint);
      return { src, dst, offset: rotation(src).invert().multiply(sourceNeutral).multiply(targetNeutral.clone().invert()).multiply(rotation(dst)) };
    }));
  const arms = targetArm.slice(0, 2).map((dst, i) => {
    const rest = rotation(dst);
    return { dst, rest, direction: position(targetArm[i + 1]).sub(position(dst)).normalize() };
  });
  return { arms, sourceArm, sourcePalm, hand: targetArm[2], handOffset: targetNeutral.invert().multiply(rotation(targetArm[2])), fingers };
});

const mixer = new AnimationMixer(snow.root);
const action = mixer.clipAction(animation);
action.setLoop(LoopOnce, 1);
action.clampWhenFinished = true;
action.play();
const samples = Array.from({ length: Math.round(animation.duration * 30) + 1 }, (_, i) => i / 30);
function key(bone, absolute) {
  bone.quaternion.copy(rotation(bone.parent).invert().multiply(absolute)).normalize();
  const values = outputTracks.get(bone) ?? [];
  const current = bone.quaternion.clone();
  if (values.length && current.dot(new Quaternion().fromArray(values, values.length - 4)) < 0) {
    current.set(-current.x, -current.y, -current.z, -current.w);
  }
  values.push(...current.toArray());
  outputTracks.set(bone, values);
}
for (const time of samples) {
  mixer.setTime(time);
  for (const { arms, sourceArm, sourcePalm, hand, handOffset, fingers } of mappings) {
    arms.forEach(({ dst, rest, direction }, index) => {
      const sourceDirection = position(sourceArm[index + 1]).sub(position(sourceArm[index])).normalize();
      key(dst, new Quaternion().setFromUnitVectors(direction, sourceDirection).multiply(rest));
    });
    const handBasis = palm(sourcePalm);
    key(hand, handBasis.clone().multiply(handOffset));
    // Both rigs now face the same way. Apply the rest-frame correction per digit.
    for (const { src, dst, offset } of fingers) key(dst, rotation(src).multiply(offset));
  }
}

const { doc } = target;
const chunks = [target.bin];
let byteOffset = target.bin.length;
function accessor(values, type, count) {
  const data = Buffer.alloc(values.length * 4);
  values.forEach((value, i) => data.writeFloatLE(value, i * 4));
  const bufferView = doc.bufferViews.push({ buffer: 0, byteOffset, byteLength: data.length }) - 1;
  chunks.push(data);
  byteOffset += data.length;
  return doc.accessors.push({ bufferView, type, count, componentType: 5126,
    ...(type === 'SCALAR' ? { min: [0], max: [samples.at(-1)] } : {}) }) - 1;
}
const input = accessor(samples, 'SCALAR', samples.length);
const result = { name: clip.name, samplers: [], channels: [] };
for (const [node, values] of outputTracks) {
  const output = accessor(values, 'VEC4', samples.length);
  const sampler = result.samplers.push({ input, output, interpolation: 'LINEAR' }) - 1;
  result.channels.push({ sampler, target: { node: vrm.nodes.indexOf(node), path: 'rotation' } });
}
doc.animations = [result];
doc.buffers[0].byteLength = byteOffset;
const json = Buffer.from(JSON.stringify(doc));
const padded = Buffer.concat([json, Buffer.alloc((4 - json.length % 4) % 4, 32)]);
const header = Buffer.alloc(20);
[0x46546c67, 2, 28 + padded.length + byteOffset, padded.length, 0x4e4f534a].forEach((v, i) => header.writeUInt32LE(v, i * 4));
const binHeader = Buffer.alloc(8);
binHeader.writeUInt32LE(byteOffset);
binHeader.writeUInt32LE(0x004e4942, 4);
writeFileSync(outputPath, Buffer.concat([header, padded, binHeader, ...chunks]));
console.log(`Wrote ${result.channels.length} animated bones with ${samples.length} samples`);
