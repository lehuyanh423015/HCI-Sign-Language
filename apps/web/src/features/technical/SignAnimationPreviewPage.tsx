import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

const PILOT_URL = '/models/technical/tech-pose-authoring-pilot.glb';

export function SignAnimationPreviewPage() {
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">Automated pose authoring · TASK-0010</p>
        <h2>Pose authoring pilot preview</h2>
        <p className="technical-warning">TECHNICAL_FIXTURE_NOT_A_SIGN</p>
        <p>
          Fixture kỹ thuật này kiểm tra pose library, animation dữ liệu hóa và xuất GLB; không thuộc S001–S006 và không phải nội dung VSL đã xác minh.
          Pilot ký hiệu thật vẫn bị chặn vì repository chưa có reference hợp lệ.
        </p>
        <dl className="preview-review-status" data-testid="sign-preview-review-status">
          <div><dt>ID</dt><dd>TECHNICAL_FIXTURE_NOT_A_SIGN</dd></div>
          <div><dt>Master</dt><dd>1.0.0</dd></div>
          <div><dt>Primary clip</dt><dd>TECH_POSE_AUTHORING_PILOT</dd></div>
          <div><dt>Technical</dt><dd>PASS — automated pose fixture</dd></div>
          <div><dt>Linguistic</dt><dd>NOT_APPLICABLE — fixture</dd></div>
          <div><dt>Real sign pilot</dt><dd>BLOCKED — reference required</dd></div>
        </dl>
      </div>
      <TechnicalViewer
        modelUrl={PILOT_URL}
        clipName="TECH_POSE_AUTHORING_PILOT"
        classification="TECHNICAL_FIXTURE_NOT_A_SIGN · linguistic NOT_APPLICABLE"
      />
    </article>
  );
}
