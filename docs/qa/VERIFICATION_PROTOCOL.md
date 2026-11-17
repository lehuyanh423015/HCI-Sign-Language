# Quy trình xác minh

## Trạng thái kết quả

- `PASS`: check đã thực sự chạy và đạt, có command/version/evidence.
- `FAIL`: check chạy và lỗi hoặc prerequisite sai.
- `SKIPPED`: không chạy do không áp dụng/thiếu công cụ; không được tính PASS.
- `NOT YET TESTED`: nằm trong scope sau nhưng chưa có đối tượng/evidence.

## Ba lớp độc lập

1. **Automated structural:** schema, ID/path/clip, GLB header, mesh/skin, skeleton signature, build/tests.
2. **Manual technical:** browser playback controls, 0.5×/1×, loop/reset, camera, material, texture, clipping/deformation, front/side views.
3. **Content/expert:** reference provenance, regional variant, motion/timing correctness, reviewer reference và evidence thật.

Không lớp nào thay thế lớp khác. Automated PASS không cho phép đánh `approved` nếu expert verification thiếu.

## Evidence record tối thiểu

Sign ID/revision, date/timezone, animator, master commit/hash, Blender/MPFB/exporter version, command/check output, reviewer reference, reference source, findings, decision, required correction, artifact link/hash. Không ghi reviewer giả; nếu chưa có dùng `null` và status phù hợp.

## User testing

Ngày 12–13 chỉ cho người dùng xem `approved` animation. Draft kỹ thuật có thể dùng nội bộ với cảnh báo nhưng không dùng để đo learning/usability của nội dung. Ghi consent/protocol theo yêu cầu môn học và tránh thu thập dữ liệu không cần thiết.

## Milestone gates

- Day 3: browser playback kỹ thuật thật, không cần tuyên bố correctness giáo dục.
- Day 5: đánh giá throughput, expert availability và lỗi rig để quyết định 6 hoặc giảm 3–4; tối đa 8 chỉ khi có dư thời gian.
- Day 10: workflow tích hợp và animation gửi verification.
- Day 12–13: user testing approved-only.
- Day 15: demo/evidence/tests/presentation.

TASK-0001 không đánh dấu milestone nào hoàn thành.
