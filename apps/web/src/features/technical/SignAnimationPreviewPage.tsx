import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

const S001_DRAFT_FILE = 's001-snow.glb';
const S001_DRAFT_URL = `/models/technical/${S001_DRAFT_FILE}`;

export function SignAnimationPreviewPage() {
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
          <div><dt>Avatar</dt><dd>Snow v4.2</dd></div>
          <div><dt>Tệp mô hình</dt><dd>{S001_DRAFT_FILE}</dd></div>
          <div><dt>Hoạt ảnh</dt><dd>S001_MAIN</dd></div>
          <div><dt>Chuyển động</dt><dd>Bản chuyển từ clip kỹ thuật S001 phiên bản 4</dd></div>
          <div><dt>Ngôn ngữ</dt><dd>NOT YET TESTED</dd></div>
          <div><dt>Xuất bản</dt><dd>LOCAL STAGING ONLY — educational publication NOT APPROVED</dd></div>
          <div><dt>Nguồn avatar</dt><dd>Snow Rig (CC) Blender Foundation | <a href="https://studio.blender.org/characters/snow/v4/">studio.blender.org</a></dd></div>
        </dl></details>
      </div>
      <TechnicalViewer
        modelUrl={S001_DRAFT_URL}
        clipName="S001_MAIN"
        classification="SIGN_PRODUCTION_CANDIDATE · technical draft · linguistic NOT YET TESTED"
      />
    </article>
  );
}
