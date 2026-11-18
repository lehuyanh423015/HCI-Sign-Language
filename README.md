# Hệ thống học Ngôn ngữ Ký hiệu Việt Nam với avatar 3D

Monorepo dùng chung cho nhóm HCI bốn thành viên. TASK-0001 chỉ dựng nền tảng kỹ thuật: web shell, hợp đồng dữ liệu/3D/adaptive, kiểm tra tự động và quy trình cộng tác. Repository **chưa chứa animation ký hiệu đã xác minh**.

## Master Avatar v1.0.0

`blender/master/avatar_master.blend` là **Temporary Technical Release** đã được owner duyệt về hình ảnh và suitability cho development. Release giữ 137 bones, sáu core `NMM_` Morph Targets, eye/finger controls và technical Actions. Các Action/GLB demo chỉ là technical fixtures; trạng thái phê duyệt nội dung Ngôn ngữ Ký hiệu Việt Nam vẫn là `NOT YET TESTED`.

- Manifest: `blender/master/master-avatar.manifest.json`.
- Release package: `assets/releases/master-avatar-v1/`.
- Handoff: `docs/team/MASTER_V1_HANDOFF.md`.
- Release notes: `docs/releases/MASTER_AVATAR_V1.md`.

> Mọi fixture hiển thị trong web hiện tại là **“Technical placeholder - not verified sign language.”** Chỉ nội dung có `reviewStatus: "approved"` và đủ bằng chứng mới được dùng cho học tập hoặc user testing.

## Bắt đầu nhanh trên Windows CMD

Yêu cầu: Node.js 24 LTS (khuyến nghị 24.22.2), npm 11, Git 2.45+.

```cmd
npm ci
npm run sync:data
npm run dev
```

Mở URL Vite in ra terminal. Kiểm tra toàn bộ nền tảng:

```cmd
npm run doctor
npm run check
```

Baseline 3D chính thức là Blender 5.2.4 LTS + MPFB 2.0.18. `doctor` có thể báo `SKIPPED` trên máy frontend không cài Blender; điều này không chặn web development. Xem [cài đặt Windows](docs/setup/SETUP_WINDOWS.md) và [cài đặt Blender](docs/setup/SETUP_BLENDER.md).

## Lệnh chính

| Lệnh | Mục đích |
|---|---|
| `npm run dev` | Chạy web development server |
| `npm run build` | Type-check và tạo production build |
| `npm run lint` | Kiểm tra TypeScript/React source |
| `npm run typecheck` | Kiểm tra kiểu TypeScript |
| `npm run test` | Chạy data contract tests và web smoke tests |
| `npm run validate:data` | Kiểm tra schema, ID, asset path và approval policy |
| `npm run sync:data` | Validate rồi sao chép nguồn dữ liệu canonical vào web |
| `npm run validate:assets` | Kiểm tra GLB hiện có; asset chưa làm được ghi `NOT YET TESTED` |
| `npm run sync:technical-assets` | Đồng bộ canonical technical GLB vào web public directory |
| `npm run validate:technical-asset` | Kiểm tra clip, skin, channels, duration và Khronos validation |
| `npm run validate:master-v1` | Kiểm tra static/technical GLB, manifests, hashes và Khronos validation của Master v1 |
| `npm run doctor` | Báo môi trường và prerequisite |
| `npm run check` | Chạy quality gate không cần Blender/MPFB |

## Nguồn sự thật và ranh giới

- Metadata: `data/*.json`; không sửa bản sinh trong `apps/web/public/data/`.
- Canonical Master Avatar v1.0.0: `blender/master/avatar_master.blend`. `blender/avatar_master.blend` là legacy source; không di chuyển hay ghi đè.
- Export review: `assets/exports/signs/`; chỉ publish GLB đã qua gate vào `apps/web/public/models/signs/`.
- Hợp đồng tích hợp: `docs/contracts/`; mọi thay đổi cần phối hợp các owner liên quan.

Xem [kiến trúc](docs/architecture/OVERVIEW.md), [ownership](docs/team/OWNERSHIP.md), [handoff](docs/team/HANDOFF.md) và [Git workflow](docs/workflows/GIT_WORKFLOW.md).

Prototype kỹ thuật: chạy `npm run sync:technical-assets`, `npm run dev`, rồi mở `/technical-viewer`. Đây không phải nội dung Ngôn ngữ Ký hiệu Việt Nam đã xác minh.

## Mốc dự án (chưa hoàn thành trong TASK-0001)

- Ngày 3: một animation kỹ thuật chạy trong browser.
- Ngày 5: quyết định giữ 6 signs hay giảm còn 3–4.
- Ngày 10: tích hợp learning/quiz/review; gửi animation xác minh.
- Ngày 12–13: user testing chỉ với animation giáo dục đã duyệt.
- Ngày 15: demo tích hợp, evidence, tests và presentation.
