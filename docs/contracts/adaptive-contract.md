# Hợp đồng adaptive learning

Đây là rule-based demonstration, **không phải tuyên bố sư phạm đã được kiểm chứng**. Owner: Do Phuong Thao; consumer chính: frontend của Doan Khanh Nhat.

## Kiểu dữ liệu tối thiểu

```ts
type AnswerResult = 'correct' | 'wrong';

interface ReviewHistoryEntry {
  userId: string;
  signId: string;
  correctStreak: number;
  wrongStreak: number;
  lastResult: AnswerResult | null;
  lastReviewedAt: string | null; // ISO 8601
  nextReviewAt: string | null;   // ISO 8601
}

interface ReviewCandidate extends ReviewHistoryEntry {
  priority: number; // số lớn được xếp trước
  due: boolean;
}
```

## Rules

- **AD-01:** một câu sai tạo/cập nhật entry, đặt `wrongStreak = previous wrongStreak + 1`, `correctStreak = 0`, đưa sign vào review và đặt `nextReviewAt` đến hạn ngay.
- **AD-02:** khi `wrongStreak >= 2`, tăng priority so với entry chỉ sai một lần. Không để priority âm.
- **AD-03:** với câu trả lời trong review, hai câu đúng liên tiếp đặt `wrongStreak = 0`, giảm priority và dời `nextReviewAt` xa hơn. Khoảng ngày cụ thể phải là hằng số có test và được ghi chú là demo.
- **AD-04:** đầu session, chọn entry cùng `userId` có `nextReviewAt <= now`, cộng entry chưa có due date cần review; sắp theo priority giảm dần rồi due date tăng dần. Hàm nhận `now` từ caller để test deterministic.

## API pure functions đề xuất

```ts
applyAnswer(entry, result, now, policy): ReviewHistoryEntry
buildReviewList(history, userId, now): ReviewCandidate[]
parseStoredHistory(raw): { history: ReviewHistoryEntry[]; recovered: boolean }
```

Không đọc LocalStorage bên trong core rules. Adapter frontend mới chịu trách nhiệm persistence.

## LocalStorage

- Namespace: `hci-vsl:adaptive:v1:<userId>`.
- Envelope: `{ "version": 1, "updatedAt": "<ISO>", "entries": [...] }`.
- Demo profile tách bằng stable `userId` do UI chọn, ví dụ `demo-a`; không có authentication.
- JSON thiếu/sai type/version: không crash. Backup raw value trong memory/log development, khởi tạo mảng rỗng và báo UI rằng lịch sử đã được reset. Không silently coi dữ liệu hỏng là hợp lệ.
- Không trộn history giữa profile. Không lưu dữ liệu nhạy cảm.

## Input/output và lỗi

Input phải có sign ID tồn tại trong metadata; streak là integer không âm; timestamp ISO. Core function trả object mới, không mutate input. Unknown sign, timestamp sai hoặc result ngoài enum là validation error và không ghi storage.

## Kiểm thử

Table-driven unit tests cho từng rule, chuyển tiếp streak, boundary `nextReviewAt == now`, sorting, user separation, corrupted JSON, migration version và timezone. Thêm integration test UI → adapter → pure function → LocalStorage. Educational effectiveness cần nghiên cứu riêng và nằm ngoài unit test.
