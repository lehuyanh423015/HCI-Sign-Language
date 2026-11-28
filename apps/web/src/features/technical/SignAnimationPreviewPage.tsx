import { useState } from 'react';
import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

const avatars = {
  snow: { name: 'Khang', model: 'Snow v4.2', file: 's001-snow.glb' },
  vroid: { name: 'Linh', model: 'AvatarSample_A (VRoid)', file: 's001-vroid.glb' },
};

const animations = {
  greeting: { label: 'Xin chào', practice: undefined },
  lift: { label: 'Luyện nâng tay', practice: { label: 'Luyện nâng tay', range: [0, 0.54] as const } },
  wave: { label: 'Luyện vẫy tay', practice: { label: 'Luyện vẫy tay', range: [0.54, 1.53] as const } },
};

export function SignAnimationPreviewPage() {
  const [selection, setSelection] = useState<keyof typeof avatars>('snow');
  const [mode, setMode] = useState<keyof typeof animations>('greeting');
  const avatar = avatars[selection];
  const animation = animations[mode];
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">Xem trước kỹ thuật</p>
        <h1>S001 — Xin chào</h1>
        <p className="technical-warning">Bản mẫu kỹ thuật · Chờ xác minh ngôn ngữ</p>
        <p>
          Chọn tốc độ 0,5× để quan sát chuyển động tay, hoặc xoay nhân vật để xem từ góc khác.
        </p>
        <details><summary>Thông tin bản dựng và kiểm chứng</summary><dl className="preview-review-status" data-testid="sign-preview-review-status">
          <div><dt>ID</dt><dd>S001</dd></div>
          <div><dt>Biến thể</dt><dd>Hà Nội</dd></div>
          <div><dt>Avatar</dt><dd>{avatar.name} · {avatar.model}</dd></div>
          <div><dt>Tệp mô hình</dt><dd>{avatar.file}</dd></div>
          <div><dt>Hoạt ảnh</dt><dd>{animation.label} · S001_MAIN</dd></div>
          <div><dt>Chuyển động</dt><dd>Bản chuyển từ clip kỹ thuật S001 phiên bản 4</dd></div>
          <div><dt>Ngôn ngữ</dt><dd>NOT YET TESTED</dd></div>
          <div><dt>Xuất bản</dt><dd>LOCAL STAGING ONLY — educational publication NOT APPROVED</dd></div>
          <div><dt>Nguồn avatar</dt><dd>{selection === 'snow'
            ? <>Snow Rig (CC) Blender Foundation | <a href="https://studio.blender.org/characters/snow/v4/">studio.blender.org</a></>
            : 'VRoid Project'}</dd></div>
        </dl></details>
      </div>
      <div className="preview-picker">
        <fieldset className="preview-avatar-picker">
          <legend>Nhân vật</legend>
          <div className="preview-avatar-options">
            {(Object.keys(avatars) as (keyof typeof avatars)[]).map((id) => (
              <label className="preview-avatar-card" key={id}>
                <input type="radio" name="preview-avatar" value={id} checked={selection === id}
                  onChange={() => setSelection(id)} />
                <span className={`preview-avatar-initial preview-avatar-initial--${id}`} aria-hidden="true">{avatars[id].name[0]}</span>
                <span><strong>{avatars[id].name}</strong><small>{avatars[id].model}</small></span>
              </label>
            ))}
          </div>
        </fieldset>
        <label className="preview-animation-select">
          Hoạt ảnh
          <select value={mode} onChange={(event) => setMode(event.target.value as keyof typeof animations)}>
            {Object.entries(animations).map(([id, { label }]) => <option key={id} value={id}>{label}</option>)}
          </select>
        </label>
      </div>
      <TechnicalViewer
        key={`${selection}:${mode}`}
        modelUrl={`/models/technical/${avatar.file}`}
        clipName="S001_MAIN"
        practice={animation.practice}
        classification="SIGN_PRODUCTION_CANDIDATE · technical draft · linguistic NOT YET TESTED"
      />
    </article>
  );
}
