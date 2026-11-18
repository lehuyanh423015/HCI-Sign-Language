import { useEffect, useRef, useState } from 'react';
import {
  AnimationAction,
  AnimationMixer,
  Box3,
  Color,
  DirectionalLight,
  HemisphereLight,
  LoopOnce,
  LoopRepeat,
  Mesh,
  Object3D,
  PerspectiveCamera,
  Scene,
  SRGBColorSpace,
  Vector3,
  WebGLRenderer,
} from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export const TECHNICAL_MODEL_URL = '/models/technical/technical-hand-test-neutral.glb';
export const TECHNICAL_CLIP_NAME = 'TECH_HAND_CONTROL_TEST';

type TechnicalViewerProps = {
  modelUrl?: string;
  clipName?: string;
  classification?: string;
};

type ViewerStatus = 'loading' | 'ready' | 'error';

function normalizedNodeName(object: Object3D) {
  return object.name.replace(/[^a-z0-9]/gi, '').toLowerCase();
}

function findSemanticNodes(model: Object3D, names: Set<string>) {
  const found = new Map<string, Object3D>();
  model.traverse((object) => {
    const normalized = normalizedNodeName(object);
    if (names.has(normalized)) found.set(normalized, object);
  });
  return found;
}

function skeletonBasis(model: Object3D) {
  const wanted = new Set(['shoulder01l', 'shoulder01r', 'head', 'pelvis']);
  const nodes = findSemanticNodes(model, wanted);
  if (nodes.size !== wanted.size) {
    return { up: new Vector3(0, 1, 0), forward: new Vector3(0, 0, 1) };
  }
  const left = nodes.get('shoulder01l')!.getWorldPosition(new Vector3());
  const right = nodes.get('shoulder01r')!.getWorldPosition(new Vector3());
  const head = nodes.get('head')!.getWorldPosition(new Vector3());
  const pelvis = nodes.get('pelvis')!.getWorldPosition(new Vector3());
  const lateral = left.sub(right).normalize();
  const up = head.sub(pelvis).normalize();
  const forward = lateral.cross(up).normalize();
  return { up, forward };
}

export function TechnicalViewer({
  modelUrl = TECHNICAL_MODEL_URL,
  clipName = TECHNICAL_CLIP_NAME,
  classification = 'TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE',
}: TechnicalViewerProps = {}) {
  const mountRef = useRef<HTMLDivElement>(null);
  const actionRef = useRef<AnimationAction | null>(null);
  const mixerRef = useRef<AnimationMixer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const cameraRef = useRef<PerspectiveCamera | null>(null);
  const modelRef = useRef<Object3D | null>(null);
  const [status, setStatus] = useState<ViewerStatus>('loading');
  const [statusMessage, setStatusMessage] = useState('Đang tải technical GLB…');
  const [playing, setPlaying] = useState(true);
  const [looping, setLooping] = useState(true);
  const [speed, setSpeed] = useState<0.5 | 1>(1);
  const [animationTime, setAnimationTime] = useState(0);
  const [cameraPreset, setCameraPreset] = useState<'full' | 'hand'>('full');
  const [clipNames, setClipNames] = useState<string[]>([]);

  const frameModel = (handPreset = false) => {
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    const model = modelRef.current;
    if (!camera || !controls || !model) return false;

    if (handPreset) {
      // GLTFLoader sanitizes Blender node names; match semantic names defensively.
      const wanted = new Set(['wristr', 'finger21r', 'finger51r']);
      const handNodes = findSemanticNodes(model, wanted);
      if (handNodes.size === wanted.size) {
        const target = [...handNodes.values()]
          .map((object) => object.getWorldPosition(new Vector3()))
          .reduce((sum, point) => sum.add(point), new Vector3())
          .multiplyScalar(1 / handNodes.size);
        const { up, forward } = skeletonBasis(model);
        controls.target.copy(target);
        camera.position.copy(target).addScaledVector(forward, 0.42).addScaledVector(up, 0.02);
        camera.lookAt(target);
        controls.update();
        return true;
      }
      return false;
    }

    const bounds = new Box3().setFromObject(model);
    const center = bounds.getCenter(new Vector3());
    const size = bounds.getSize(new Vector3());
    const distance = Math.max(size.x, size.y, size.z) * 1.25;
    const { up, forward } = skeletonBasis(model);
    controls.target.copy(center);
    camera.position.copy(center).addScaledVector(forward, distance).addScaledVector(up, size.y * 0.08);
    camera.near = Math.max(distance / 100, 0.01);
    camera.far = distance * 20;
    camera.updateProjectionMatrix();
    controls.update();
    controls.saveState();
    return true;
  };

  const applyCameraPreset = (preset: 'full' | 'hand') => {
    if (frameModel(preset === 'hand')) setCameraPreset(preset);
  };

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;
    let disposed = false;
    let animationFrame = 0;
    let lastUiUpdate = 0;

    const scene = new Scene();
    scene.background = new Color(0x172421);
    const camera = new PerspectiveCamera(42, 1, 0.01, 100);
    cameraRef.current = camera;
    const renderer = new WebGLRenderer({ antialias: true, alpha: false });
    renderer.outputColorSpace = SRGBColorSpace;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.minDistance = 0.15;
    controls.maxDistance = 8;
    controlsRef.current = controls;

    scene.add(new HemisphereLight(0xffffff, 0x31433d, 2.4));
    const keyLight = new DirectionalLight(0xffffff, 3.2);
    keyLight.position.set(3, 4, 5);
    scene.add(keyLight);

    const resize = () => {
      const width = Math.max(mount.clientWidth, 1);
      const height = Math.max(mount.clientHeight, 1);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(mount);
    resize();

    const loader = new GLTFLoader();
    loader.load(
      modelUrl,
      (gltf) => {
        if (disposed) return;
        setClipNames(gltf.animations.map((item) => item.name));
        const clip = gltf.animations.find((item) => item.name === clipName);
        if (!clip) {
          setStatus('error');
          setStatusMessage(`Không tìm thấy clip ${clipName}.`);
          return;
        }
        modelRef.current = gltf.scene;
        scene.add(gltf.scene);
        const mixer = new AnimationMixer(gltf.scene);
        const action = mixer.clipAction(clip);
        action.setLoop(LoopRepeat, Infinity);
        action.clampWhenFinished = true;
        action.play();
        mixer.timeScale = 1;
        mixerRef.current = mixer;
        actionRef.current = action;
        frameModel();
        setStatus('ready');
        setStatusMessage(`Sẵn sàng · ${clip.name} · ${clip.duration.toFixed(2)}s`);
      },
      (event) => {
        if (disposed || !event.total) return;
        setStatusMessage(`Đang tải technical GLB… ${Math.round((event.loaded / event.total) * 100)}%`);
      },
      (error) => {
        if (disposed) return;
        setStatus('error');
        setStatusMessage(`Không thể tải technical GLB: ${error instanceof Error ? error.message : 'unknown error'}`);
      },
    );

    let previousTime = performance.now();
    const render = (time: number) => {
      if (disposed) return;
      const delta = Math.min(Math.max((time - previousTime) / 1000, 0), 0.1);
      previousTime = time;
      mixerRef.current?.update(delta);
      controls.update();
      renderer.render(scene, camera);
      if (time - lastUiUpdate > 150) {
        setAnimationTime(actionRef.current?.time ?? 0);
        lastUiUpdate = time;
      }
      animationFrame = requestAnimationFrame(render);
    };
    animationFrame = requestAnimationFrame(render);

    return () => {
      disposed = true;
      cancelAnimationFrame(animationFrame);
      resizeObserver.disconnect();
      controls.dispose();
      actionRef.current?.stop();
      mixerRef.current?.stopAllAction();
      modelRef.current?.traverse((object) => {
        if (object instanceof Mesh) {
          object.geometry.dispose();
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          materials.forEach((material) => material.dispose());
        }
      });
      renderer.dispose();
      renderer.domElement.remove();
      actionRef.current = null;
      mixerRef.current = null;
      controlsRef.current = null;
      cameraRef.current = null;
      modelRef.current = null;
    };
  }, [clipName, modelUrl]);

  const togglePlayback = () => {
    const action = actionRef.current;
    if (!action) return;
    action.paused = playing;
    setPlaying(!playing);
  };

  const replay = () => {
    const action = actionRef.current;
    if (!action) return;
    action.paused = false;
    action.reset().play();
    setPlaying(true);
  };

  const toggleLoop = () => {
    const action = actionRef.current;
    if (!action) return;
    const nextLooping = !looping;
    action.setLoop(nextLooping ? LoopRepeat : LoopOnce, nextLooping ? Infinity : 1);
    action.clampWhenFinished = !nextLooping;
    setLooping(nextLooping);
  };

  const toggleSpeed = () => {
    const nextSpeed = speed === 1 ? 0.5 : 1;
    if (mixerRef.current) mixerRef.current.timeScale = nextSpeed;
    setSpeed(nextSpeed);
  };

  const disabled = status !== 'ready';
  return (
    <section className="technical-viewer" aria-label="Technical Three.js animation viewer">
      <div ref={mountRef} className="technical-canvas" data-testid="technical-canvas" data-camera-preset={cameraPreset} />
      <div className={`viewer-runtime-status ${status}`} role="status" data-testid="viewer-status">
        {statusMessage}
      </div>
      <div className="runtime-metrics" aria-label="Animation runtime metrics">
        Runtime: <output data-testid="animation-time">{animationTime.toFixed(2)}s</output> · View: {cameraPreset}
      </div>
      <div className="technical-asset-metadata" data-testid="technical-asset-metadata">
        <strong>{classification}</strong>
        <span>Clips: <output data-testid="technical-clip-list">{clipNames.join(', ') || 'Đang tải…'}</output></span>
      </div>
      <div className="technical-controls" aria-label="Điều khiển technical animation">
        <button type="button" onClick={togglePlayback} disabled={disabled}>{playing ? 'Tạm dừng' : 'Tiếp tục'}</button>
        <button type="button" onClick={replay} disabled={disabled}>Phát lại</button>
        <button type="button" onClick={toggleLoop} disabled={disabled}>Loop: {looping ? 'Bật' : 'Tắt'}</button>
        <button type="button" onClick={toggleSpeed} disabled={disabled}>Tốc độ: {speed}×</button>
        <button type="button" onClick={() => applyCameraPreset('full')} disabled={disabled}>Đặt lại camera</button>
        <button type="button" onClick={() => applyCameraPreset('hand')} disabled={disabled}>Cận cảnh tay phải</button>
      </div>
    </section>
  );
}
