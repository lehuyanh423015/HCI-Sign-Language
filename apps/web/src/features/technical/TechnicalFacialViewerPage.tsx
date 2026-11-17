import { TechnicalFacialViewer } from '../../components/viewer/TechnicalFacialViewer';

export function TechnicalFacialViewerPage() {
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">Blender → GLB → Three.js · TASK-0006</p>
        <h2>Facial &amp; non-manual marker foundation</h2>
        <p className="technical-warning">TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE</p>
        <p>Trang cô lập để kiểm tra Morph Target, eye bones và clip tay–mặt. Không thuộc lesson catalog và không mang ý nghĩa ngôn ngữ đã xác minh.</p>
      </div>
      <TechnicalFacialViewer />
    </article>
  );
}
