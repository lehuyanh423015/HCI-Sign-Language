import { ViewerPlaceholder } from '../../components/viewer/ViewerPlaceholder';

export function LessonPage() {
  return (
    <article>
      <div className="page-heading">
        <p className="eyebrow">Bài học mẫu</p>
        <h2>Kiểm tra ranh giới tích hợp 3D</h2>
        <p>Không có chuyển động ký hiệu hoặc nội dung giáo dục nào được tạo trong TASK-0001.</p>
      </div>
      <ViewerPlaceholder signId="S001" />
    </article>
  );
}
