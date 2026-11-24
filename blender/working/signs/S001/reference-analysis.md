# S001 — Phân tích reference “Xin chào”

- Biến thể: Hà Nội
- Nguồn: `https://www.youtube.com/watch?v=4avGnxaLmb0`
- Timestamp gốc do owner chỉ định: `00:04–00:08`
- Local media: `references/xin_chao-owner-provided.mp4`
- Take dùng để author: local `00:03.05–00:05.00`; take đối chiếu: `00:00.35–00:02.00`
- Quyết định: `SUFFICIENT_FOR_TECHNICAL_DRAFT_NOT_LINGUISTIC_APPROVAL`

## Quan sát chính

| Thành phần | Trạng thái | Quan sát |
|---|---|---|
| Camera/perfomer | OBSERVED | Performer chính diện, upper body và hai tay nhìn rõ. |
| Tay trội | OBSERVED | Hai tay cùng tham gia, chuyển động gần đối xứng; không xác định một tay trội riêng. |
| Start | OBSERVED | Hai tay thấp trước lower torso, sau đó tách ra ngoài và nâng lên. |
| Handshape | OBSERVED | Hai bàn tay mở, năm ngón duỗi/xòe, ngón cái dạng; có natural flex. |
| Palm | OBSERVED | Lòng bàn tay nhìn chung hướng camera trong khoảng raised/oscillation. |
| Wrist | OBSERVED | Hai cổ tay/bàn tay đổi nghiêng qua lại, tạo oscillation cục bộ. |
| Arm/elbow | OBSERVED | Upper arms dạng nhẹ, elbows gập để đưa tay lên lateral shoulder/face space. |
| Path | OBSERVED | Low center → outward/up → oscillation gần vai → down/recovery. |
| Repetition | NEEDS_CONFIRMATION | Ít nhất hai lần đổi nghiêng rõ; số cycle mang nghĩa ngôn ngữ chưa được reviewer xác nhận. |
| Contact | OBSERVED | Không chạm cơ thể. |
| Head/gaze | OBSERVED | Head gần upright, gaze chủ yếu về camera. |
| Face/NMM | NEEDS_CONFIRMATION | Smile và mouth articulation hiện rõ nhưng có thể là presentation/speech, chưa đủ để gắn NMM lexical. |

## Key poses

1. Neutral pre-sign — local 03.05s.
2. Lift outward — local 03.30s.
3. Initial open/raised — local 03.55s.
4. Oscillation A — local 03.80s.
5. Oscillation B — local 04.10s.
6. Oscillation A2 — local 04.40s.
7. Final open — local 04.60s.
8. Recovery — local 05.00s.

## Unknown/assumptions bắt buộc giữ

- Exact depth và local Euler angles của arms/wrists là `ASSUMED_TECHNICAL`, không phải observed 3D measurement.
- Exact finger joint curvature ở frame motion blur là `UNKNOWN`; draft dùng open-hand technical control gần nhất.
- Exact repetition count cần qualified linguistic reviewer.
- Draft không author facial Morph Target; gaze/head giữ neutral vì NMM role chưa xác minh.
- Neutral entry/recovery là transition của video, không được gọi là lexical interval.

## Sufficiency decision

Hai take 60 FPS nhất quán, hands không bị occlude đáng kể, handshape/palm/location/path/timing đọc được. Reference đủ để tạo một `TECHNICAL_DRAFT` phục vụ owner review. Nó không đủ để tuyên bố linguistic accuracy hoặc approval; draft phải giữ `linguistic_status: NOT YET TESTED` và không vào lesson catalog.
