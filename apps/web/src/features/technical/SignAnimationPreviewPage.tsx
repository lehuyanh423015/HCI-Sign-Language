import { useState } from 'react';
import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

const avatars = {
  snow: { name: 'Snow v4.2', file: 's001-snow.glb' },
  vroid: { name: 'AvatarSample_A (VRoid)', file: 's001-vroid.glb' },
};

export function SignAnimationPreviewPage() {
  const [selection, setSelection] = useState<keyof typeof avatars>('snow');
  const avatar = avatars[selection];
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
          <div><dt>Avatar</dt><dd>{avatar.name}</dd></div>
          <div><dt>Tệp mô hình</dt><dd>{avatar.file}</dd></div>
          <div><dt>Hoạt ảnh</dt><dd>S001_MAIN</dd></div>
          <div><dt>Chuyển động</dt><dd>Bản chuyển từ clip kỹ thuật S001 phiên bản 4</dd></div>
          <div><dt>Ngôn ngữ</dt><dd>NOT YET TESTED</dd></div>
          <div><dt>Xuất bản</dt><dd>LOCAL STAGING ONLY — educational publication NOT APPROVED</dd></div>
          <div><dt>Nguồn avatar</dt><dd>{selection === 'snow'
            ? <>Snow Rig (CC) Blender Foundation | <a href="https://studio.blender.org/characters/snow/v4/">studio.blender.org</a></>
            : 'VRoid Project'}</dd></div>
        </dl></details>
      </div>
      <label className="preview-avatar-select">
        Nhân vật
        <select value={selection} onChange={(event) => setSelection(event.target.value as keyof typeof avatars)}>
          {Object.entries(avatars).map(([id, { name }]) => <option key={id} value={id}>{name}</option>)}
        </select>
      </label>
      <TechnicalViewer
        key={selection}
        modelUrl={`/models/technical/${avatar.file}`}
        clipName="S001_MAIN"
        classification="SIGN_PRODUCTION_CANDIDATE · technical draft · linguistic NOT YET TESTED"
      />
    </article>
  );
}
