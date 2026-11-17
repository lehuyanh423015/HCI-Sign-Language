# Ownership và trách nhiệm

Ownership là người review/chịu trách nhiệm, không phải quyền làm việc cô lập. Shared contract change phải báo các consumer trước khi merge.

| Thành viên | Primary ownership | Deliverables |
|---|---|---|
| **Le Huy Anh — 3D Lead** | `blender/master/`, `blender/scripts/`, rig/export standard, GLB contract | approved master revision, 3 sign working sources, export/preflight evidence, technical GLB handoff |
| **Le Quang Mien — 3D Animator** | `blender/working/mien/`, assigned S004–S006, animation previews | 3 sign `.blend`, `front/side` previews, correction notes; không ghi đè master |
| **Doan Khanh Nhat — Frontend/UI-UX** | `apps/web/`, viewer integration, routing/UI | lesson/viewer controls, quiz/review UI, GLTFLoader playback, build/browser evidence |
| **Do Phuong Thao — Adaptive/Content/QA** | `data/`, adaptive logic, references/evidence, `docs/qa/` | metadata có nguồn, adaptive tests, expert verification record, usability/QA evidence |

## Shared/review-required

- `schemas/`, `docs/contracts/`: owner tạo thay đổi + consumer liên quan review.
- `assets/exports/signs/`, production `apps/web/public/models/signs/`: Huy Anh technical gate, Thao content gate, Nhat browser gate.
- `blender/master/`: Huy Anh owns; thay rest pose/bone hierarchy cần thông báo Mien + Nhat và ADR nếu ảnh hưởng contract.
- architecture/dependency/CI: Nhat triển khai, cả nhóm được thông báo; thay Blender baseline cần Huy Anh.

## Không sửa độc lập

- Không rename bone/rest pose/master rig.
- Không sửa generated `apps/web/public/data/*.json`; sửa `data/` rồi sync.
- Không đổi ID/clip/path contract để che lỗi export.
- Không đánh `approved`, điền reviewer/evidence/source giả.
- Không merge hai version cùng `.blend`; dùng ownership lock.
