import { Link, useSearchParams } from "react-router-dom";
import { History } from "lucide-react";
import { useLearning } from "../../app/LearningState";
import { dueEntries } from "../adaptive/history";
import { demoQuestions, demoTitle } from "../lessons/catalog";
import { DataMessage } from "../lessons/LessonPage";
export function ReviewPage() {
  const s = useLearning();
  const [p] = useSearchParams();
  const demo = p.get("demo") === "1";
  const suffix = demo ? "&demo=1" : "";
  const history = s.entries.filter((e) =>
    demo
      ? demoQuestions.some((q) => q.signId === e.signId)
      : s.signs.some((x) => x.id === e.signId),
  );
  const due = dueEntries(history, s.profile, new Date());
  const name = (id: string) =>
    demo ? demoTitle(id) : s.signs.find((x) => x.id === id)?.label;
  return (
    <>
      <h1>{demo ? "Lịch ôn minh họa" : "Ôn tập cá nhân"}</h1>
      <p>
        Lịch ôn được lưu riêng trên thiết bị cho hồ sơ{" "}
        {s.profile === "demo-b" ? "B" : "A"}.
      </p>
      <DataMessage />
      <section className="panel">
        <History />
        <h2>
          {due.length
            ? "Đến hạn hôm nay"
            : history.length
              ? "Bạn đã ôn xong hôm nay"
              : "Bạn chưa có lịch sử học"}
        </h2>
        {due.map((e) => (
          <div className="listrow" key={e.signId}>
            <div>
              <b>{name(e.signId)}</b>
              <p>
                {e.wrongStreak
                  ? "Bạn đã trả lời sai " + e.wrongStreak + " lần liên tiếp."
                  : "Ôn lại để củng cố lần trả lời đúng."}
              </p>
            </div>
            <Link
              className="primary"
              to={
                "/quiz?review=1&sign=" + encodeURIComponent(e.signId) + suffix
              }
            >
              Ôn ngay
            </Link>
          </div>
        ))}
        {!history.length && (
          <Link to={demo ? "/demo" : "/lessons"}>
            {demo ? "Thử mô phỏng" : "Đến thư viện bài học"}
          </Link>
        )}
      </section>
      {!!history.length && (
        <section className="panel">
          <h2>Lịch sử trả lời</h2>
          {[...history]
            .sort((a, b) =>
              (b.lastReviewedAt ?? "").localeCompare(a.lastReviewedAt ?? ""),
            )
            .map((e) => (
              <div className="listrow" key={e.signId}>
                <div>
                  <b>{name(e.signId)}</b>
                  <p>
                    Lần gần nhất:{" "}
                    {e.lastResult === "correct" ? "Đúng" : "Chưa đúng"} ·{" "}
                    {new Date(e.lastReviewedAt!).toLocaleString("vi-VN")}
                  </p>
                </div>
                <span>
                  Hẹn ôn:{" "}
                  {new Date(e.nextReviewAt!).toLocaleDateString("vi-VN")}
                </span>
              </div>
            ))}
        </section>
      )}
      {!demo && (
        <Link className="textlink" to="/demo">
          Thử mô phỏng với hồ sơ A/B
        </Link>
      )}
    </>
  );
}
