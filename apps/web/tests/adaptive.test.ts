import { describe, expect, it } from "vitest";
import {
  applyAnswer,
  dueEntries,
  readEntries,
} from "../src/features/adaptive/history";
import { approved } from "../src/features/lessons/catalog";
import type { SignMetadata } from "../src/types/sign";
const now = new Date("2026-11-28T00:00:00Z");
describe("quy tắc ôn tập", () => {
  it("ưu tiên sai hai lần, tách hồ sơ và giãn lịch sau hai lần ôn đúng", () => {
    const once = applyAnswer(undefined, "a", "one", "wrong", false, now);
    const twice = applyAnswer(
      { ...once, signId: "two" },
      "a",
      "two",
      "wrong",
      true,
      now,
    );
    expect(
      dueEntries([once, twice, { ...once, userId: "b" }], "a", now).map(
        (e) => e.signId,
      ),
    ).toEqual(["two", "one"]);
    const first = applyAnswer(twice, "a", "two", "correct", true, now);
    const second = applyAnswer(first, "a", "two", "correct", true, now);
    expect(second.wrongStreak).toBe(0);
    expect(dueEntries([second], "a", now)).toEqual([]);
    expect(
      dueEntries([second], "a", new Date(now.getTime() + 86400000)),
    ).toHaveLength(1);
  });
  it("kiểm tra phiên bản, dữ liệu hỏng và hồ sơ", () => {
    expect(readEntries(null, "a")).toEqual([]);
    for (const raw of ["{", '{"version":2}', '{"version":1,"entries":[{}]}'])
      expect(() => readEntries(raw, "a")).toThrow();
    const entry = applyAnswer(undefined, "a", "one", "wrong", false, now);
    const raw = JSON.stringify({ version: 1, entries: [entry] });
    expect(readEntries(raw, "a")).toEqual([entry]);
    expect(() => readEntries(raw, "b")).toThrow();
  });
  it("loại bản nháp và bản thiếu minh chứng", () => {
    const valid = {
      reviewStatus: "approved",
      label: "A",
      description: "B",
      referenceSource: "C",
      durationSeconds: 2,
      reviewerReference: "R",
      verificationEvidence: ["E"],
    } as SignMetadata;
    expect(approved(valid)).toBe(true);
    expect(approved({ ...valid, reviewStatus: "draft" })).toBe(false);
    expect(approved({ ...valid, verificationEvidence: [] })).toBe(false);
  });
});
