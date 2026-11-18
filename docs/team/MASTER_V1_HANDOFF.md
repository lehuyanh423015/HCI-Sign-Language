# Master Avatar v1 — Team handoff

## Release reference

- Repository: `https://github.com/lehuyanh423015/HCI-Sign-Language.git`
- Release tag: `master-avatar-v1.0.0`
- Release title: `Master Avatar v1.0.0 — Technical Foundation`
- Canonical source: `blender/master/avatar_master.blend`
- Canonical manifest: `blender/master/master-avatar.manifest.json`
- Classification: `Temporary Technical Release`
- Technical validation: `PASS`
- Owner visual approval: `APPROVED`
- Vietnamese Sign Language content approval: `NOT YET TESTED`

Technical fixtures trong release không phải bài học hoặc ký hiệu đã xác minh.

## Fresh clone trên Windows CMD

```cmd
git clone https://github.com/lehuyanh423015/HCI-Sign-Language.git
cd HCI-Sign-Language
git switch main
git pull --ff-only
git describe --tags --exact-match
npm ci
npm run sync:data
npm run sync:technical-assets
npm run check
npm run dev
```

Mở `http://localhost:5173/technical-facial-viewer`. Trang phải tiếp tục hiển thị cảnh báo `TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE`.

## Công cụ theo vai trò

| Thành viên | Git + Node/npm | Blender 5.2.4 + MPFB 2.0.18 | Trách nhiệm chính |
|---|---|---|---|
| Le Huy Anh | Required | Required | canonical master, rig/export validators, S001–S003 |
| Le Quang Mien | Required | Required | working copies, S004–S006; không đổi master rig |
| Doan Khanh Nhat | Required | Optional | React, Three.js, UI/UX; không cần Blender cho công việc web thường ngày |
| Do Phuong Thao | Required | Optional | references, metadata, adaptive rules, linguistic/QA evidence |

## Tạo Blender working copy an toàn

Không save trực tiếp canonical master. Trong Windows CMD:

```cmd
mkdir blender\working\<member>\<task-or-sign>
copy /Y blender\master\avatar_master.blend blender\working\<member>\<task-or-sign>\Snnn.blend
certutil -hashfile blender\working\<member>\<task-or-sign>\Snnn.blend SHA256
```

Ghi tag/commit, SHA-256, Blender/MPFB version và owner lock vào handoff của animation. Không rename/reparent bones, apply armature transform, đổi rest pose hoặc đổi tên sáu core `NMM_` targets.

## Export và validation

Production sign dùng `Snnn_MAIN`, 30 FPS, frame 1 neutral và export self-contained GLB theo `docs/contracts/3d-asset-contract.md`.

```cmd
npm run validate:assets
npm run validate:master-v1
npm run sync:technical-assets
npm run sync:technical-assets:check
npm run check
```

Static release asset ở `assets/releases/master-avatar-v1/master-avatar-v1-static.glb`. Technical demo có single source of truth ở `assets/exports/technical/task-0007a/technical-facial-refined-test.glb`; browser copy được sinh tự động, không sửa trực tiếp.

## Submit animation

1. Tạo branch riêng từ `main`, ví dụ `feat/3d-huy-anh-s001` hoặc `feat/3d-mien-s004`.
2. Dùng working `.blend`, không sửa canonical master.
3. Export `assets/exports/signs/Snnn.glb` và tạo front/side evidence.
4. Ghi master tag/commit/hash, clip, FPS/frame range và known issues.
5. Chạy automated checks; Huy Anh review technical compatibility.
6. Thao điều phối source/linguistic evidence. Không đặt `reviewStatus: "approved"` nếu thiếu qualified review.
7. Nhat chỉ đưa asset vào lesson runtime sau technical + content + browser gates.

## Update sign metadata

Sửa canonical JSON trong `data/`, không sửa file sinh trong `apps/web/public/data/`:

```cmd
npm run validate:data
npm run sync:data
npm run sync:data:check
```

ID `Snnn` chỉ là khóa kỹ thuật cho tới khi có source và evidence được duyệt.

## Git LFS và binary

Master v1 không dùng LFS pointer; file lớn nhất hiện khoảng 6 MB và dưới giới hạn 100 MB/file của GitHub. Fresh clone phải nhận binary thật và kiểm tra hash trong release manifest. Không bật LFS hoặc migrate history nếu chưa có PR riêng, backup và xác nhận của cả bốn máy.

## Issue và Pull Request

Issue blocker ghi: owner, file/sign ID, master tag/commit/hash, expected/actual, log/evidence, ảnh hưởng và quyết định cần có.

```cmd
git switch main
git pull --ff-only
git switch -c <type>/<short-name>
npm ci
npm run check
git status --short
git push -u origin <type>/<short-name>
```

PR phải liệt kê commands thật sự đã chạy, binary/hash liên quan, `PASS`/`FAIL`/`SKIPPED`/`NOT YET TESTED`, reviewers cần thiết và không chứa cache, credential hoặc user-local path.

## Acceptance còn lại

- Huy Anh: xác nhận master lock và export workflow trên máy chính — `PENDING` cho lần checkout mới.
- Mien: clone, Blender preflight và working-copy hash — `PENDING`.
- Nhat: clone, `npm ci`, browser runtime — `PENDING`.
- Thao: clone, data/QA workflow và linguistic gate — `PENDING`.

Không suy ra team onboarding đã hoàn thành từ automated release checks.
