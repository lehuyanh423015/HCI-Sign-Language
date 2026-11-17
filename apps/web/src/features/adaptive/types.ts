export type AnswerResult = 'correct' | 'wrong';

export interface ReviewHistoryEntry {
  userId: string;
  signId: string;
  correctStreak: number;
  wrongStreak: number;
  lastResult: AnswerResult | null;
  lastReviewedAt: string | null;
  nextReviewAt: string | null;
}

export interface ReviewCandidate extends ReviewHistoryEntry {
  priority: number;
  due: boolean;
}
