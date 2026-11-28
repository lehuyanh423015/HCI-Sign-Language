import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

const S001_DRAFT_URL = '/models/technical/s001-xin-chao-task-0011b-refined.glb';

export function SignAnimationPreviewPage() {
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">Xem trước kỹ thuật · Phiên bản 4</p>
        <h1>S001 — Xin chào</h1>
        <p className="technical-warning">Bản mẫu kỹ thuật · Chờ xác minh ngôn ngữ</p>
        <p>
          Quan sát bàn tay và nét mặt. Chọn tốc độ 0,5× để xem chậm, hoặc xoay nhân vật để xem từ góc khác.
        </p>
        <details><summary>Thông tin bản dựng và kiểm chứng</summary><dl className="preview-review-status" data-testid="sign-preview-review-status">
          <div><dt>ID</dt><dd>S001</dd></div>
          <div><dt>Biến thể</dt><dd>Hà Nội</dd></div>
          <div><dt>Master</dt><dd>1.0.0</dd></div>
          <div><dt>Tệp mô hình</dt><dd>s001-xin-chao-task-0011b-refined.glb</dd></div>
          <div><dt>Hoạt ảnh</dt><dd>S001_MAIN</dd></div>
          <div><dt>Kỹ thuật</dt><dd>PASS — owner accepted prototype 2026-11-24</dd></div>
          <div><dt>Ngôn ngữ</dt><dd>NOT YET TESTED</dd></div>
          <div><dt>Xuất bản</dt><dd>LOCAL STAGING ONLY — educational publication NOT APPROVED</dd></div>
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
