import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

const S001_DRAFT_URL = '/models/technical/s001-xin-chao-task-0011b-refined.glb';

export function SignAnimationPreviewPage() {
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">S001 reference-driven refined candidate · TASK-0011B</p>
        <h2>S001 — Xin chào</h2>
        <p className="technical-warning">TECHNICAL DRAFT — NOT LINGUISTICALLY APPROVED</p>
        <p>
          Bản dựng cục bộ dựa trên video tham chiếu do chủ dự án cung cấp. Trang này chỉ dùng để kiểm tra chuyển động,
          camera và bàn tay; nội dung chưa được người có chuyên môn xác nhận và chưa thuộc catalog bài học đã duyệt.
        </p>
        <dl className="preview-review-status" data-testid="sign-preview-review-status">
          <div><dt>ID</dt><dd>S001</dd></div>
          <div><dt>Variant</dt><dd>Hà Nội</dd></div>
          <div><dt>Master</dt><dd>1.0.0</dd></div>
          <div><dt>Asset</dt><dd>s001-xin-chao-task-0011b-refined.glb</dd></div>
          <div><dt>Primary clip</dt><dd>S001_MAIN</dd></div>
          <div><dt>Technical</dt><dd>PASS — owner accepted prototype 2026-11-24</dd></div>
          <div><dt>Linguistic</dt><dd>NOT YET TESTED</dd></div>
          <div><dt>Publication</dt><dd>LOCAL STAGING ONLY — educational publication NOT APPROVED</dd></div>
        </dl>
      </div>
      <TechnicalViewer
        modelUrl={S001_DRAFT_URL}
        clipName="S001_MAIN"
        classification="SIGN_PRODUCTION_CANDIDATE · technical draft · linguistic NOT YET TESTED"
      />
    </article>
  );
}
