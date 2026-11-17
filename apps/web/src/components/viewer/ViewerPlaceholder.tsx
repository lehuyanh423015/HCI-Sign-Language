export interface ViewerPlaceholderProps {
  signId?: string;
}

export function ViewerPlaceholder({ signId }: ViewerPlaceholderProps) {
  return (
    <section className="viewer-placeholder" aria-label="Khu vực trình diễn avatar 3D">
      <div className="viewer-grid" aria-hidden="true" />
      <div className="viewer-message">
        <span className="status-pill">Chưa có GLB</span>
        <h2>{signId ?? '3D Viewer'}</h2>
        <p>Technical placeholder - not verified sign language.</p>
      </div>
      <div className="viewer-controls" aria-label="Điều khiển dự kiến">
        <button type="button" disabled>Phát / Tạm dừng</button>
        <button type="button" disabled>Phát lại</button>
        <button type="button" disabled>0.5× / 1×</button>
        <button type="button" disabled>Đặt lại camera</button>
      </div>
    </section>
  );
}
