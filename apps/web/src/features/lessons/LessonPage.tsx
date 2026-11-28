import { useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import {
  BookOpen,
  Box,
  ChevronRight,
  History,
  Play,
  Scan,
  Repeat2,
  SlidersHorizontal,
  FlaskConical,
} from "lucide-react";
import { TechnicalViewer } from "../../components/viewer/TechnicalViewer";
import { useLearning } from "../../app/LearningState";
import { dueEntries } from "../adaptive/history";

export function DataMessage() {
  const s = useLearning();
  return (
    <>
      {s.loading && <p role="status">Đang tải học liệu…</p>}
      {s.error && (
        <p role="alert">
          Không tải được học liệu. <button onClick={s.retry}>Thử lại</button>
        </p>
      )}
      {s.notice && <p role="status">{s.notice}</p>}
    </>
  );
}
export function Home() {
  const s = useLearning();
  const due = dueEntries(s.entries, s.profile, new Date()).filter((e) =>
    s.signs.some((x) => x.id === e.signId),
  );
  const resume = s.signs.find((x) => x.id === s.resume);
  const target = due.length
    ? "/review"
    : resume
      ? "/lessons/" + resume.id
      : s.signs.length
        ? "/lessons/" + s.signs[0].id
        : "/technical-sign-preview";
  const action = due.length
    ? "Ôn hôm nay"
    : resume
      ? "Tiếp tục học"
      : s.signs.length
        ? "Bắt đầu học"
        : "Xem bản mẫu 3D";
  return (
    <>
      <div className="intro">
        <h1>Không gian học tập</h1>
        <p>Học Ngôn ngữ Ký hiệu Việt Nam qua chuyển động 3D.</p>
      </div>
      <DataMessage />
      <section className="hero">
        <div className="hero-copy">
          <span className="hero-label">
            <Box size={16} /> {s.signs.length ? "Bài học 3D" : "Trải nghiệm 3D"}
          </span>
          <h2>
            {due.length
              ? "Đến giờ ôn tập"
              : resume
                ? "Tiếp tục bài học"
                : "Quan sát từng chuyển động"}
          </h2>
          <p>
            {due.length
              ? due.length + " ký hiệu đã đến hạn ôn."
              : resume
                ? resume.label
                : "Xoay nhân vật, xem chậm và lặp lại để theo dõi bàn tay và nét mặt từ nhiều góc nhìn."}
          </p>
          <Link className="primary" to={target}>
            <Play size={17} />
            {action}
          </Link>
        </div>
        <div className="hero-art">
          <div className="orbit" />
          <img
            src="/images/linh-preview.webp"
            alt="Nhân vật 3D Linh đang vẫy tay"
          />
          <span>
            <Box size={14} /> Linh · Avatar 3D
          </span>
        </div>
      </section>
      <h2 className="section-title">Học và luyện tập</h2>
      <div className="tiles">
        <Link to="/lessons" className="tile">
          <span className="tile-icon">
            <BookOpen />
          </span>
          <div>
            <h3>Thư viện bài học</h3>
            <p>
              {s.signs.length
                ? s.signs.length + " ký hiệu đã duyệt"
                : "Khám phá ký hiệu theo chủ đề"}
            </p>
          </div>
          <ChevronRight />
        </Link>
        <Link to="/review" className="tile">
          <span className="tile-icon violet">
            <History />
          </span>
          <div>
            <h3>Ôn tập cá nhân</h3>
            <p>Xem lịch ôn và lịch sử trả lời</p>
          </div>
          <ChevronRight />
        </Link>
      </div>
      <section className="guide">
        <h2>Làm quen với trình xem</h2>
        <div className="tips">
          {([
            [Scan, "Quan sát", "Giữ mặt và hai tay trong khung."],
            [SlidersHorizontal, "Xem chậm", "Chọn tốc độ 0,5× để theo dõi."],
            [Repeat2, "Lặp lại", "Xem lại chuyển động theo nhịp riêng."],
          ] as const).map(([Icon, title, desc]) => {
            return (
              <div key={title}>
                <Icon />
                <div>
                  <strong>{title}</strong>
                  <p>{desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>
      <Link className="textlink" to="/demo">
        <FlaskConical size={16} /> Mở mô phỏng ôn tập
      </Link>
    </>
  );
}
export function Library() {
  const s = useLearning();
  return (
    <>
      <h1>Thư viện bài học</h1>
      <p>Chọn ký hiệu để quan sát và luyện nhận biết.</p>
      <DataMessage />
      {s.signs.length ? (
        <section className="panel">
          <h2>Ký hiệu cơ bản</h2>
          {s.signs.map((sign) => {
            const entry = s.entries.find((e) => e.signId === sign.id);
            return (
              <Link
                className="listrow"
                key={sign.id}
                to={"/lessons/" + sign.id}
              >
                <b>{sign.label}</b>
                <span>
                  {entry?.wrongStreak
                    ? "Cần ôn"
                    : entry
                      ? "Đã học"
                      : "Chưa học"}
                </span>
              </Link>
            );
          })}
        </section>
      ) : (
        !s.loading &&
        !s.error && (
          <div className="panel empty">
            <BookOpen />
            <h2>Học liệu đang được kiểm chứng</h2>
            <p>
              Các ký hiệu sẽ xuất hiện ở đây sau khi được duyệt. Bạn có thể khám
              phá cách điều khiển nhân vật ngay trong bản mẫu.
            </p>
            <Link className="primary" to="/technical-sign-preview">
              Xem bản mẫu 3D
            </Link>
          </div>
        )
      )}
    </>
  );
}
export function LessonPage() {
  const { id } = useParams();
  const s = useLearning();
  const sign = s.signs.find((x) => x.id === id);
  const remember = s.remember;
  useEffect(() => {
    if (sign && s.resume !== sign.id) remember(sign.id);
  }, [sign, s.resume, remember]);
  if (!sign)
    return (
      <>
        <DataMessage />
        {!s.loading && <Link to="/lessons">Về thư viện bài học</Link>}
      </>
    );
  return (
    <>
      <h1>{sign.label}</h1>
      <div className="lesson-grid">
        <TechnicalViewer
          key={sign.id}
          learner
          modelUrl={"/" + sign.glbPath}
          clipName={sign.animationClip}
        />
        <aside className="panel">
          <h2>Thông tin ký hiệu</h2>
          <p>{sign.description}</p>
          <p>Biến thể: {sign.regionalVariant}</p>
          <p>Nguồn: {sign.referenceSource}</p>
          {s.questions.some((q) => q.signId === id) ? (
            <Link className="primary" to={"/quiz?sign=" + id}>
              Kiểm tra nhận biết
            </Link>
          ) : (
            <p>Câu hỏi đang được chuẩn bị.</p>
          )}
        </aside>
      </div>
    </>
  );
}
