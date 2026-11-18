import { useEffect, useRef, useState } from 'react';
import {
  AnimationAction,
  AnimationMixer,
  Box3,
  Color,
  DirectionalLight,
  Euler,
  HemisphereLight,
  LoopOnce,
  LoopRepeat,
  Mesh,
  Object3D,
  PerspectiveCamera,
  Quaternion,
  Scene,
  SRGBColorSpace,
  Vector3,
  WebGLRenderer,
} from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export const FACIAL_MODEL_URL = '/models/technical/master-avatar-v1-technical-demo.glb';
export const FACIAL_DEFAULT_CLIP = 'TECH_HAND_FACE_TEST';

type ViewerStatus = 'loading' | 'ready' | 'error';
type CameraPreset = 'full' | 'face';
type GazePreset = 'center' | 'left' | 'right' | 'up' | 'down';
type MorphBinding = { mesh: Mesh; index: number };

function findByNormalizedName(model: Object3D, expected: string) {
  const normalized = expected.replace(/[^a-z0-9]/gi, '').toLowerCase();
  let found: Object3D | undefined;
  model.traverse((object) => {
    if (object.name.replace(/[^a-z0-9]/gi, '').toLowerCase() === normalized) found = object;
  });
  return found;
}

export function TechnicalFacialViewer() {
  const mountRef = useRef<HTMLDivElement>(null);
  const mixerRef = useRef<AnimationMixer | null>(null);
  const actionRef = useRef<AnimationAction | null>(null);
  const actionsRef = useRef(new Map<string, AnimationAction>());
  const controlsRef = useRef<OrbitControls | null>(null);
  const cameraRef = useRef<PerspectiveCamera | null>(null);
  const modelRef = useRef<Object3D | null>(null);
  const morphBindingsRef = useRef(new Map<string, MorphBinding[]>());
  const eyeBonesRef = useRef<Array<{ object: Object3D; neutral: Quaternion }>>([]);
  const [status, setStatus] = useState<ViewerStatus>('loading');
  const [statusMessage, setStatusMessage] = useState('Đang tải facial GLB…');
  const [morphNames, setMorphNames] = useState<string[]>([]);
  const [morphValues, setMorphValues] = useState<Record<string, number>>({});
  const [clipNames, setClipNames] = useState<string[]>([]);
  const [activeClip, setActiveClip] = useState(FACIAL_DEFAULT_CLIP);
  const [playing, setPlaying] = useState(true);
  const [looping, setLooping] = useState(true);
  const [speed, setSpeed] = useState<0.5 | 1>(1);
  const [animationTime, setAnimationTime] = useState(0);
  const [cameraPreset, setCameraPreset] = useState<CameraPreset>('face');
  const [gazePreset, setGazePreset] = useState<GazePreset>('center');

  const frameModel = (preset: CameraPreset) => {
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    const model = modelRef.current;
    if (!camera || !controls || !model) return false;
    const bounds = new Box3().setFromObject(model);
    const center = bounds.getCenter(new Vector3());
    const size = bounds.getSize(new Vector3());
    if (preset === 'face') {
      const head = findByNormalizedName(model, 'head');
      if (!head) return false;
      const target = head.getWorldPosition(new Vector3()).add(new Vector3(0, size.y * 0.04, 0));
      controls.target.copy(target);
      camera.position.copy(target).add(new Vector3(0, size.y * 0.02, size.y * 0.34));
    } else {
      controls.target.copy(center);
      camera.position.copy(center).add(new Vector3(0, size.y * 0.06, size.y * 1.35));
    }
    camera.near = 0.01;
    camera.far = Math.max(size.y * 20, 20);
    camera.updateProjectionMatrix();
    camera.lookAt(controls.target);
    controls.update();
    controls.saveState();
    setCameraPreset(preset);
    return true;
  };

  const applyMorph = (name: string, value: number) => {
    for (const binding of morphBindingsRef.current.get(name) ?? []) {
      if (binding.mesh.morphTargetInfluences) binding.mesh.morphTargetInfluences[binding.index] = value;
    }
    setMorphValues((current) => ({ ...current, [name]: value }));
  };

  const applyGaze = (preset: GazePreset) => {
    const angles: Record<GazePreset, [number, number]> = {
      center: [0, 0], left: [0, 0.12], right: [0, -0.12], up: [-0.08, 0], down: [0.08, 0],
    };
    const [vertical, horizontal] = angles[preset];
    const offset = new Quaternion().setFromEuler(new Euler(vertical, 0, horizontal));
    for (const eye of eyeBonesRef.current) eye.object.quaternion.copy(eye.neutral).multiply(offset);
    setGazePreset(preset);
  };

  const playClip = (name: string) => {
    const next = actionsRef.current.get(name);
    if (!next) return;
    actionRef.current?.stop();
    next.reset();
    next.paused = false;
    next.setLoop(looping ? LoopRepeat : LoopOnce, looping ? Infinity : 1);
    next.clampWhenFinished = !looping;
    next.play();
    actionRef.current = next;
    setActiveClip(name);
    setPlaying(true);
  };

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;
    let disposed = false;
    let animationFrame = 0;
    let lastUiUpdate = 0;
    const scene = new Scene();
    scene.background = new Color(0x15231f);
    const camera = new PerspectiveCamera(38, 1, 0.01, 100);
    cameraRef.current = camera;
    const renderer = new WebGLRenderer({ antialias: true });
    renderer.outputColorSpace = SRGBColorSpace;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.minDistance = 0.08;
    controls.maxDistance = 8;
    controlsRef.current = controls;
    scene.add(new HemisphereLight(0xffffff, 0x30423c, 2.6));
    const light = new DirectionalLight(0xffffff, 3.4);
    light.position.set(3, 4, 5);
    scene.add(light);

    const resize = () => {
      const width = Math.max(mount.clientWidth, 1);
      const height = Math.max(mount.clientHeight, 1);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(mount);
    resize();

    new GLTFLoader().load(
      FACIAL_MODEL_URL,
      (gltf) => {
        if (disposed) return;
        modelRef.current = gltf.scene;
        scene.add(gltf.scene);
        const bindings = new Map<string, MorphBinding[]>();
        gltf.scene.traverse((object) => {
          if (!(object instanceof Mesh) || !object.morphTargetDictionary || !object.morphTargetInfluences) return;
          for (const [name, index] of Object.entries(object.morphTargetDictionary)) {
            if (!name.startsWith('NMM_')) continue;
            const rows = bindings.get(name) ?? [];
            rows.push({ mesh: object, index });
            bindings.set(name, rows);
          }
        });
        morphBindingsRef.current = bindings;
        const names = [...bindings.keys()].sort();
        setMorphNames(names);
        setMorphValues(Object.fromEntries(names.map((name) => [name, 0])));
        eyeBonesRef.current = ['eye.L', 'eye.R']
          .map((name) => findByNormalizedName(gltf.scene, name))
          .filter((object): object is Object3D => Boolean(object))
          .map((object) => ({ object, neutral: object.quaternion.clone() }));
        const mixer = new AnimationMixer(gltf.scene);
        mixerRef.current = mixer;
        actionsRef.current = new Map(gltf.animations.map((clip) => [clip.name, mixer.clipAction(clip)]));
        const namesOfClips = gltf.animations.map((clip) => clip.name);
        setClipNames(namesOfClips);
        const initial = actionsRef.current.get(FACIAL_DEFAULT_CLIP);
        if (!initial || names.length === 0 || eyeBonesRef.current.length !== 2) {
          setStatus('error');
          setStatusMessage('GLB thiếu clip, NMM Morph Target hoặc eye bones bắt buộc.');
          return;
        }
        initial.setLoop(LoopRepeat, Infinity).play();
        initial.clampWhenFinished = false;
        actionRef.current = initial;
        mixer.timeScale = 1;
        frameModel('face');
        setStatus('ready');
        setStatusMessage(`Sẵn sàng · ${FACIAL_MODEL_URL.split('/').at(-1)} · ${names.length} NMM targets`);
      },
      (event) => {
        if (!disposed && event.total) setStatusMessage(`Đang tải facial GLB… ${Math.round((event.loaded / event.total) * 100)}%`);
      },
      (error) => {
        if (!disposed) {
          setStatus('error');
          setStatusMessage(`Không thể tải facial GLB: ${error instanceof Error ? error.message : 'unknown error'}`);
        }
      },
    );

    let previous = performance.now();
    const render = (time: number) => {
      if (disposed) return;
      const delta = Math.min(Math.max((time - previous) / 1000, 0), 0.1);
      previous = time;
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
      observer.disconnect();
      controls.dispose();
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
      actionsRef.current.clear();
      morphBindingsRef.current.clear();
      eyeBonesRef.current = [];
    };
  }, []);

  const togglePlayback = () => {
    if (!actionRef.current) return;
    actionRef.current.paused = playing;
    setPlaying(!playing);
  };
  const replay = () => {
    if (!actionRef.current) return;
    actionRef.current.paused = false;
    actionRef.current.reset().play();
    setPlaying(true);
  };
  const toggleLoop = () => {
    if (!actionRef.current) return;
    const next = !looping;
    actionRef.current.setLoop(next ? LoopRepeat : LoopOnce, next ? Infinity : 1);
    actionRef.current.clampWhenFinished = !next;
    setLooping(next);
  };
  const toggleSpeed = () => {
    const next = speed === 1 ? 0.5 : 1;
    if (mixerRef.current) mixerRef.current.timeScale = next;
    setSpeed(next);
  };
  const resetAll = () => {
    actionRef.current?.stop();
    for (const name of morphNames) applyMorph(name, 0);
    applyGaze('center');
    const defaultAction = actionsRef.current.get(FACIAL_DEFAULT_CLIP);
    if (defaultAction) {
      defaultAction.reset();
      defaultAction.paused = true;
      defaultAction.play();
      actionRef.current = defaultAction;
    }
    setActiveClip(FACIAL_DEFAULT_CLIP);
    setPlaying(false);
    setAnimationTime(0);
    frameModel('full');
  };

  const disabled = status !== 'ready';
  return (
    <section className="facial-viewer-shell" aria-label="Technical facial Three.js viewer">
      <div className="facial-stage">
        <div ref={mountRef} className="facial-canvas" data-testid="facial-canvas" data-camera-preset={cameraPreset} data-gaze-preset={gazePreset} />
        <div className={`viewer-runtime-status ${status}`} role="status" data-testid="facial-viewer-status">{statusMessage}</div>
        <div className="runtime-metrics">Runtime: <output data-testid="facial-animation-time">{animationTime.toFixed(2)}s</output> · {activeClip}</div>
        <div className="facial-camera-controls">
          <button type="button" onClick={() => frameModel('full')} disabled={disabled}>Toàn thân</button>
          <button type="button" onClick={() => frameModel('face')} disabled={disabled}>Cận cảnh mặt</button>
          <button type="button" onClick={resetAll} disabled={disabled}>Đặt lại tất cả</button>
        </div>
      </div>
      <aside className="facial-control-panel">
        <section>
          <h3>Morph Targets</h3>
          <p className="control-summary" data-testid="morph-target-list">{morphNames.join(', ') || 'Đang tải…'}</p>
          {morphNames.map((name) => (
            <label className="morph-control" key={name}>
              <span>{name}</span><output>{(morphValues[name] ?? 0).toFixed(2)}</output>
              <input data-testid={`morph-${name}`} type="range" min="0" max="1" step="0.01" value={morphValues[name] ?? 0} disabled={disabled} onChange={(event) => applyMorph(name, Number(event.target.value))} />
            </label>
          ))}
        </section>
        <section>
          <h3>Gaze</h3>
          <div className="button-grid" data-testid="gaze-controls">
            {(['center', 'left', 'right', 'up', 'down'] as GazePreset[]).map((preset) => <button type="button" key={preset} onClick={() => applyGaze(preset)} disabled={disabled}>{preset}</button>)}
          </div>
        </section>
        <section>
          <h3>Animation</h3>
          <label className="clip-select">Clip
            <select data-testid="facial-clip-select" value={activeClip} disabled={disabled} onChange={(event) => playClip(event.target.value)}>
              {clipNames.map((name) => <option key={name} value={name}>{name}</option>)}
            </select>
          </label>
          <p className="control-summary" data-testid="facial-clip-list">{clipNames.join(', ') || 'Đang tải…'}</p>
          <div className="button-grid">
            <button type="button" onClick={togglePlayback} disabled={disabled}>{playing ? 'Tạm dừng' : 'Tiếp tục'}</button>
            <button type="button" onClick={replay} disabled={disabled}>Phát lại</button>
            <button type="button" onClick={toggleLoop} disabled={disabled}>Loop: {looping ? 'Bật' : 'Tắt'}</button>
            <button type="button" onClick={toggleSpeed} disabled={disabled}>Tốc độ: {speed}×</button>
          </div>
        </section>
        <dl className="facial-status-list">
          <div><dt>File</dt><dd>master-avatar-v1-technical-demo.glb</dd></div>
          <div><dt>Playback</dt><dd data-testid="facial-playback-status">{playing ? 'playing' : 'paused'} · {speed}× · loop {looping ? 'on' : 'off'}</dd></div>
          <div><dt>Gaze</dt><dd>{gazePreset}</dd></div>
        </dl>
      </aside>
    </section>
  );
}
