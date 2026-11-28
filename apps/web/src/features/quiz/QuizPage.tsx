import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { FlaskConical, CircleCheck, CircleX } from "lucide-react";
import { useLearning } from "../../app/LearningState";
import { demoQuestions, demoTitle, type Question } from "../lessons/catalog";
import { DataMessage } from "../lessons/LessonPage";
import { TechnicalViewer } from "../../components/viewer/TechnicalViewer";
import { dueEntries } from "../adaptive/history";

type Result = { question: string; sign: string; correct: boolean };
export function DemoPage() {
  return (
    <>
      <h1>Mô phỏng ôn tập</h1>
      <div className="panel empty">
        <FlaskConical />
        <h2>Thử một lượt học minh họa</h2>
        <p>
          Quan sát hai chuyển động hình học và chọn hướng di chuyển. Dữ liệu này
          dùng để kiểm tra cách lưu kết quả, ưu tiên và giãn lịch ôn cho từng hồ
          sơ.
        </p>
        <Link className="primary" to="/quiz?demo=1">
          Bắt đầu mô phỏng
        </Link>
        <Link className="textlink" to="/review?demo=1">
          Lịch ôn minh họa
        </Link>
      </div>
    </>
  );
}
function Motion({ id }: { id: string }) {
  const [paused, setPaused] = useState(() => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  const [slow, setSlow] = useState(false);
  return (
    <div>
      <div className="motion" aria-label="Hoạt ảnh hình học">
        <span
          className={id === "demo-ngang" ? "horizontal" : "vertical"}
          style={{
            animationPlayState: paused ? "paused" : "running",
            animationDuration: slow ? "4s" : "2s",
          }}
        />
      </div>
      <div className="actions flex flex-wrap gap-2">
        <button onClick={() => setPaused(!paused)}>
          {paused ? "Phát" : "Tạm dừng"}
        </button>
        <button aria-pressed={slow} onClick={() => setSlow(!slow)}>
          Xem chậm
        </button>
      </div>
    </div>
  );
}
export function QuizPage() {
  const s = useLearning();
  const [params] = useSearchParams();
  const demo = params.get("demo") === "1";
  const review = params.get("review") === "1";
  const id = params.get("sign");
  const qs = (demo ? demoQuestions : s.questions).filter(
    (q) =>
      (!id || q.signId === id) &&
      (!review ||
        dueEntries(s.entries, s.profile, new Date()).some(
          (e) => e.signId === q.signId,
        )),
  );
  const [queue, setQueue] = useState<Question[] | null>(null);
  return (
    <>
      <h1>{demo ? "Kiểm tra minh họa" : "Kiểm tra nhận biết"}</h1>
      {demo && (
        <p className="notice">Dữ liệu mô phỏng · Chuyển động hình học</p>
      )}
      <DataMessage />
      {queue ? (
        <QuizRun queue={queue} demo={demo} review={review} />
      ) : (
        <section className="panel">
          <h2>
            {qs.length ? "Sẵn sàng quan sát?" : "Chưa có câu hỏi phù hợp"}
          </h2>
          {qs.length ? (
            <>
              <p>
                {qs.length} câu hỏi. Bạn có thể xem lại chuyển động trước khi
                chọn đáp án.
              </p>
              <button className="primary" onClick={() => setQueue(qs)}>
                Bắt đầu
              </button>
            </>
          ) : (
            <Link to={demo ? "/demo" : "/lessons"}>Quay lại</Link>
          )}
        </section>
      )}
    </>
  );
}
function QuizRun({
  queue,
  demo,
  review,
}: {
  queue: Question[];
  demo: boolean;
  review: boolean;
}) {
  const s = useLearning();
  const navigate = useNavigate();
  const [results, setResults] = useState<Result[]>([]);
  const [choice, setChoice] = useState("");
  const [checked, setChecked] = useState(false);
  const q = queue[results.length];
  const sign = s.signs.find((x) => x.id === q.signId);
  const [correct, setCorrect] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState("");
  async function confirm() {
    if (!choice || checked || saving) return;
    const id = attempt || crypto.randomUUID();
    setAttempt(id);
    setError("");
    setSaving(true);
    try {
      setCorrect(await s.answer(q, choice, review, id));
      setChecked(true);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Chưa lưu được đáp án.");
    } finally { setSaving(false); }
  }
  function next() {
    const all = [...results, { question: q.id, sign: q.signId, correct }];
    if (all.length === queue.length) {
      navigate("/results" + (demo ? "?demo=1" : ""), {
        state: { results: all, profile: s.profile },
      });
      return;
    }
    setResults(all);
    setChoice("");
    setChecked(false);
    setAttempt("");
  }
  return (
    <div className="panel">
      <p>
        Câu {results.length + 1} / {queue.length}
      </p>
      <h2>{q.prompt}</h2>
      {demo ? (
        <Motion key={q.id} id={q.signId} />
      ) : (
        sign && (
          <TechnicalViewer
            learner
            key={q.id}
            modelUrl={"/" + sign.glbPath}
            clipName={sign.animationClip}
          />
        )
      )}
      <fieldset disabled={checked || saving || !!attempt}>
        <legend>Chọn một đáp án</legend>
        {q.choices.map((c) => (
          <label className="answer" key={c.id}>
            <input
              type="radio"
              name="answer"
              checked={c.id === choice}
              onChange={() => setChoice(c.id)}
            />
            {c.label}
          </label>
        ))}
      </fieldset>
      {error && <p role="alert">{error}</p>}
      {checked ? (
        <>
          <p role="status">
            {correct
              ? "Đúng rồi."
              : "Chưa đúng. Mục này đã được thêm vào lịch ôn."}
          </p>
          <button className="primary" autoFocus onClick={next}>
            {results.length + 1 === queue.length
              ? "Xem kết quả"
              : "Câu tiếp theo"}
          </button>
        </>
      ) : (
        <button className="primary" disabled={!choice || saving} onClick={confirm}>
          {saving ? "Đang lưu…" : error ? "Thử lưu lại" : "Xác nhận"}
        </button>
      )}
    </div>
  );
}
export function ResultsPage() {
  const s = useLearning();
  const { state, search } = useLocation();
  const demo = new URLSearchParams(search).get("demo") === "1";
  const rows: Result[] = state?.profile === s.profile ? state.results : [];
  return (
    <>
      <h1>Kết quả {demo ? "minh họa" : ""}</h1>
      <div className="panel">
        <h2>
          {rows.length
            ? "Đúng " +
              rows.filter((x) => x.correct).length +
              " / " +
              rows.length +
              " câu"
            : "Chưa có kết quả trong lượt này"}
        </h2>
        {rows.map((r) => (
          <div className="listrow" key={r.question}>
            {r.correct ? <CircleCheck /> : <CircleX />}
            <b>
              {demo
                ? demoTitle(r.sign)
                : s.signs.find((x) => x.id === r.sign)?.label}
            </b>
            <span>{r.correct ? "Đúng" : "Cần ôn"}</span>
            {!r.correct && (
              <Link to={demo ? "/demo/" + r.sign : "/lessons/" + r.sign}>
                Xem lại động tác
              </Link>
            )}
          </div>
        ))}
        <Link className="primary" to={"/review" + search}>
          Xem lịch ôn
        </Link>
      </div>
    </>
  );
}
export function DemoReplay() {
  const id = useLocation().pathname.split("/").pop() ?? "";
  return (
    <>
      <h1>{demoTitle(id)}</h1>
      <p>Chuyển động hình học minh họa</p>
      <Motion id={id} />
      <Link to="/review?demo=1">Về lịch ôn minh họa</Link>
    </>
  );
}
