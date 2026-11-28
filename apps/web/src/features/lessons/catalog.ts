import type { SignMetadata } from "../../types/sign";
export interface Question {
  id: string;
  signId: string;
  prompt: string;
  choices: { id: string; label: string }[];
  correctChoiceId?: string;
  reviewStatus: string;
}
export const approved = (s: SignMetadata) =>
  s.reviewStatus === "approved" &&
  Boolean(
    s.label &&
    s.description &&
    s.referenceSource &&
    s.reviewerReference &&
    s.verificationEvidence?.length &&
    s.durationSeconds,
  );
export const demoQuestions: Question[] = ["ngang", "dọc"].map((axis, i) => ({
  id: "demo-q" + i,
  signId: "demo-" + axis,
  prompt: "Chấm tròn di chuyển theo hướng nào?",
  choices: [
    { id: "ngang", label: "Theo chiều ngang" },
    { id: "dọc", label: "Theo chiều dọc" },
  ],
  correctChoiceId: axis,
  reviewStatus: "demo",
}));
export function demoTitle(id: string) {
  return id === "demo-ngang" ? "Chuyển động ngang" : "Chuyển động dọc";
}
