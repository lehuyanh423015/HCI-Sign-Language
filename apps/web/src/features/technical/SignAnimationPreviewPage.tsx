import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

const PILOT_URL = '/models/technical/technical-sign-pipeline-pilot.glb';

export function SignAnimationPreviewPage() {
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">Staging preview · TASK-0009</p>
        <h2>Sign animation production preview</h2>
        <p className="technical-warning">TECHNICAL_FIXTURE_NOT_A_SIGN</p>
        <p>
          Pilot hạ tầng dùng fixture phi ngôn ngữ hiện có; không thuộc S001–S006 và không phải nội dung VSL đã xác minh.
          Pilot ký hiệu thật đang bị chặn do chưa có reference hợp lệ.
        </p>
        <dl className="preview-review-status" data-testid="sign-preview-review-status">
          <div><dt>ID</dt><dd>TECHNICAL_FIXTURE_NOT_A_SIGN</dd></div>
          <div><dt>Master</dt><dd>1.0.0</dd></div>
          <div><dt>Primary clip</dt><dd>TECH_HAND_FACE_TEST</dd></div>
          <div><dt>Technical</dt><dd>PASS — infrastructure fixture</dd></div>
          <div><dt>Linguistic</dt><dd>NOT YET TESTED</dd></div>
        </dl>
      </div>
      <TechnicalViewer
        modelUrl={PILOT_URL}
        clipName="TECH_HAND_FACE_TEST"
        classification="TECHNICAL_FIXTURE_NOT_A_SIGN · linguistic NOT YET TESTED"
      />
    </article>
  );
}
