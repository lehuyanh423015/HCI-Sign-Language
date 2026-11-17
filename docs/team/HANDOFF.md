# Handoff nhanh cho nhóm

## Mỗi người bắt đầu

```cmd
git clone https://github.com/lehuyanh423015/HCI-Sign-Language.git
cd HCI-Sign-Language
git switch main
git pull --ff-only
git switch -c <branch-name>
npm ci
npm run doctor
```

3D member dùng Blender 5.2.4 LTS + MPFB 2.0.18, đọc `SETUP_BLENDER.md`, tạo working copy đúng folder và báo nhóm đang giữ file nào. Web/QA member chạy `npm run check` trước khi push.

## Xem technical prototype

```cmd
npm ci
npm run sync:data
npm run sync:technical-assets
npm run validate:technical-asset
npm run dev
```

Mở `http://localhost:5173/technical-viewer`. Banner phải ghi `TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE`. Thử pause/resume, replay, loop, 0.5×/1×, rotate/zoom, reset camera và hand preset.

## Giao gì và phụ thuộc ai

- **Huy Anh:** master revision + skeleton/preflight record + S001–S003 `.blend`/preview/GLB. Mien phụ thuộc master; Nhat phụ thuộc GLB contract; Thao phụ thuộc preview/evidence.
- **Mien:** S004–S006 source/preview/GLB dựa trên đúng master revision. Huy Anh review technical trước khi Nhat tích hợp.
- **Nhat:** viewer controls, route/UI và browser playback evidence. Cần Huy Anh cung cấp clip/GLB đúng contract và Thao cung cấp metadata approval.
- **Thao:** canonical metadata, reference/evidence, adaptive rules/tests và QA result. Nhat chỉ publish educational mode sau approval.

## Asset nào được sửa

- Huy Anh/Mien chỉ sửa file trong working folder của mình. Không save trực tiếp `blender/avatar_master.blend` hoặc file animator khác.
- `assets/exports/technical/technical-hand-test.glb` là fixture pipeline; không đổi thành S001–S006.
- Nhat consume canonical GLB qua `npm run sync:technical-assets`; không commit public generated copy.
- Thao sửa canonical `data/`, source/evidence; không tự đánh `approved` thiếu reviewer.
- Shared contracts, master, production export cần review của owner/consumer liên quan.

## Integration

1. PR ngắn, đúng owner, không kèm cache/render tạm.
2. `npm run check`; 3D PR thêm `npm run validate:assets` + manual checklist.
3. Shared contract cần owner + consumer review.
4. Merge vào `main`; thành viên khác rebase/merge main sớm, không sửa binary conflict bằng text merge.

## Báo blocker

Trong group/issue ghi: `BLOCKER`, owner, sign ID/file, master commit/hash, expected/actual, log/screenshot, ảnh hưởng milestone, quyết định cần trước thời điểm nào. Không tự đổi contract hay scope. Ngày 5 dùng evidence thực tế để quyết định 6 hay 3–4 signs.

Mỗi Agent task phải kèm report theo `docs/workflows/AGENT_TASK_PROTOCOL.md`. Pull request nêu exact commands và phân biệt automated PASS với manual visual acceptance.

## Git LFS

Git LFS 3.5.1 có trên máy bootstrap và remote endpoint được nhận diện, nhưng repository chưa bật tracking patterns và remote auth/upload chưa được thử. Prototype `.blend`/`.glb` hiện dưới giới hạn GitHub; trước khi thêm nhiều video/GLB lớn, cả bốn máy phải cài `git lfs`, xác nhận remote quota/auth rồi bật patterns trong PR riêng. Không migrate history tùy tiện.
