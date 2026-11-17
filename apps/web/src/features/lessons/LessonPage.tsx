import { TechnicalViewer } from '../../components/viewer/TechnicalViewer';

export function LessonPage() {
  return (
    <article>
      <div className="page-heading technical-heading">
        <p className="eyebrow">Bản xem trước kỹ thuật 3D</p>
        <h2>Avatar giáo dục trung tính</h2>
        <p className="technical-warning">TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE</p>
        <p>
          Fixture kiểm tra rig, skinning và điều khiển runtime; không thuộc S001–S006 và
          không phải nội dung bài học đã được xác minh.
        </p>
      </div>
      <TechnicalViewer />
    </article>
  );
}
