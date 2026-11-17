import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

export function TechnicalViewerPage() {
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">Blender → GLB → Three.js</p>
        <h2>Neutral educational avatar prototype</h2>
        <p className="technical-warning">TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE</p>
        <p>Avatar trung tính với trang phục tối giản để kiểm tra bone, skinning và runtime controls. Không thuộc S001–S006 và không dùng làm nội dung học.</p>
      </div>
      <TechnicalViewer />
    </article>
  );
}
