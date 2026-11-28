import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

export function inspectGlb(filePath, expectedClip) {
  const bytes = readFileSync(filePath);
  if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF') throw new Error('invalid GLB magic header');
  if (bytes.readUInt32LE(4) !== 2) throw new Error('GLB must use glTF 2.0');
  if (bytes.readUInt32LE(8) !== bytes.length) throw new Error('declared GLB length does not match file size');
  const jsonLength = bytes.readUInt32LE(12);
  if (bytes.readUInt32LE(16) !== 0x4e4f534a) throw new Error('first GLB chunk is not JSON');
  const document = JSON.parse(bytes.toString('utf8', 20, 20 + jsonLength).replace(/\u0000+$/g, '').trim());
  const animations = document.animations ?? [];
  if (!animations.some((animation) => animation.name === expectedClip)) throw new Error(`missing animation clip ${expectedClip}`);
  if (!document.meshes?.length) throw new Error('missing mesh data');
  if (!document.skins?.length) throw new Error('missing skinning data');
  const nodes = document.nodes ?? [];
  const parentByChild = new Map();
  nodes.forEach((node, parent) => (node.children ?? []).forEach((child) => parentByChild.set(child, parent)));
  const joints = [...new Set(document.skins.flatMap((skin) => skin.joints ?? []))].sort((a, b) => a - b);
  const hierarchy = joints.map((index) => ({
    name: nodes[index]?.name ?? `#${index}`,
    parent: parentByChild.has(index) ? (nodes[parentByChild.get(index)]?.name ?? `#${parentByChild.get(index)}`) : null,
  }));
  return createHash('sha256').update(JSON.stringify(hierarchy)).digest('hex');
}
