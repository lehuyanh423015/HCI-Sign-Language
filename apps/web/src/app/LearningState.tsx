import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { api, writeApi } from "../services/api";
import { approved, type Question } from "../features/lessons/catalog";
import { readEntries, applyAnswer } from "../features/adaptive/history";
import type { SignMetadata } from "../types/sign";
import type {
  ReviewHistoryEntry,
  AnswerResult,
} from "../features/adaptive/types";

function useLearningState(profile: string, account: boolean) {
  const [signs, setSigns] = useState<SignMetadata[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [notice, setNotice] = useState("");
  const storageKey = "hci-vsl:adaptive:v1:" + profile;
  const [entries, setEntries] = useState<ReviewHistoryEntry[]>([]);
  const [resume, setResume] = useState("");
  const damagedHistory = useRef<string | null>(null);
  useEffect(() => {
    if (account) return;
    function restore() {
    let raw: string | null = null;
    try {
      setResume(localStorage.getItem(storageKey + ":resume") ?? "");
      raw = localStorage.getItem(storageKey);
      setEntries(readEntries(raw, profile));
    } catch {
      damagedHistory.current = raw;
      setEntries([]);
      setNotice(
        "Lịch sử lưu trên thiết bị không đọc được. Phiên này bắt đầu với lịch sử trống.",
      );
    }
    }
    restore();
    function sync(event: StorageEvent) {
      if (event.key === storageKey || event.key === storageKey + ":resume" || event.key === null) restore();
    }
    window.addEventListener("storage",sync);
    return () => window.removeEventListener("storage",sync);
  }, [profile, storageKey, account]);
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      api<{signs: SignMetadata[]; quizzes: Question[]}>("catalog", { signal: controller.signal }),
      account ? api<{resume: string; entries: ReviewHistoryEntry[]}>("progress", { signal: controller.signal }) : null,
    ])
      .then(([data, progress]) => {
        if (controller.signal.aborted) return;
        if (progress) { setEntries(progress.entries); setResume(progress.resume); }
        const usable = data.signs.filter(approved);
        setSigns(usable);
        setQuestions(
          data.quizzes.filter(
            (q) =>
              q.reviewStatus === "approved" &&
              usable.some((s) => s.id === q.signId),
          ),
        );
        setError(false);
      })
      .catch(() => {
        if (!controller.signal.aborted) setError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [attempt, account]);
  function remember(id: string) {
    setResume(id);
    if (account) {
      void writeApi("progress/resume", "PUT", {id}).catch(() => setNotice("Chưa lưu được bài học đang xem."));
      return;
    }
    try {
      localStorage.setItem(storageKey + ":resume", id);
    } catch {
      setNotice("Thiết bị chỉ lưu tiến độ trong phiên này.");
    }
  }
  async function answer(question: Question, choice: string, review: boolean, attempt: string) {
    if (account) {
      const { correct, entry } = await writeApi<{correct: boolean; entry: ReviewHistoryEntry}>("progress/answer", "POST", {question: question.id, choice, review, attempt});
      setEntries(previous => [...previous.filter(e => e.signId !== entry.signId), entry]);
      return correct;
    }
    const id = question.signId;
    const correct = choice === question.correctChoiceId;
    const result: AnswerResult = correct ? "correct" : "wrong";
    const now = new Date();
    const entry = applyAnswer(
      entries.find((e) => e.signId === id),
      profile,
      id,
      result,
      review,
      now,
    );
    const next = [...entries.filter((e) => e.signId !== id), entry];
    setEntries(next);
    try {
      localStorage.setItem(
        storageKey,
        JSON.stringify({
          version: 1,
          updatedAt: now.toISOString(),
          entries: next,
        }),
      );
    } catch {
      setNotice("Thiết bị chỉ lưu lịch sử trong phiên này.");
    }
    return correct;
  }
  return {
    profile,
    signs,
    questions,
    entries,
    answer,
    loading,
    error,
    notice,
    resume,
    remember,
    retry: () => {
      setLoading(true);
      setAttempt((a) => a + 1);
    },
  };
}
const Context = createContext<ReturnType<typeof useLearningState> | null>(null);
export function LearningProvider({
  profile,
  account = false,
  children,
}: {
  profile: string;
  account?: boolean;
  children: ReactNode;
}) {
  const state = useLearningState(profile, account);
  return <Context.Provider value={state}>{children}</Context.Provider>;
}
export function useLearning() {
  const state = useContext(Context);
  if (!state) throw new Error("Thiếu phiên học");
  return state;
}
