import type { AnswerResult, ReviewHistoryEntry } from "./types";

export const REVIEW_DAYS = [1, 3, 7];
export function applyAnswer(
  previous: ReviewHistoryEntry | undefined,
  userId: string,
  signId: string,
  result: AnswerResult,
  review: boolean,
  now: Date,
): ReviewHistoryEntry {
  const correctStreak =
    result === "correct" && review ? (previous?.correctStreak ?? 0) + 1 : 0;
  const wrongStreak = result === "wrong" ? (previous?.wrongStreak ?? 0) + 1 : 0;
  const days =
    correctStreak >= 2
      ? REVIEW_DAYS[Math.min(correctStreak - 2, REVIEW_DAYS.length - 1)]
      : 0;
  return {
    userId,
    signId,
    correctStreak,
    wrongStreak,
    lastResult: result,
    lastReviewedAt: now.toISOString(),
    nextReviewAt: new Date(now.getTime() + days * 86400000).toISOString(),
  };
}
export function dueEntries(
  entries: ReviewHistoryEntry[],
  user: string,
  now: Date,
) {
  return entries
    .filter(
      (e) =>
        e.userId === user &&
        (!e.nextReviewAt || Date.parse(e.nextReviewAt) <= now.getTime()),
    )
    .sort(
      (a, b) =>
        b.wrongStreak - a.wrongStreak ||
        (a.nextReviewAt ?? "").localeCompare(b.nextReviewAt ?? ""),
    );
}
const validDate = (v: unknown) =>
  v === null || (typeof v === "string" && Number.isFinite(Date.parse(v)));
export function readEntries(
  raw: string | null,
  user: string,
): ReviewHistoryEntry[] {
  if (!raw) return [];
  const value = JSON.parse(raw);
  if (
    value.version !== 1 ||
    !Array.isArray(value.entries) ||
    !value.entries.every(
      (e: ReviewHistoryEntry) =>
        e &&
        e.userId === user &&
        typeof e.signId === "string" &&
        ["wrong", "correct", null].includes(e.lastResult) &&
        Number.isInteger(e.correctStreak) &&
        e.correctStreak >= 0 &&
        Number.isInteger(e.wrongStreak) &&
        e.wrongStreak >= 0 &&
        validDate(e.nextReviewAt) &&
        validDate(e.lastReviewedAt),
    )
  )
    throw new Error("Lịch sử sai định dạng");
  return value.entries;
}
