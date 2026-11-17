# TASK-0001 — Project bootstrap report

- Ngày thực hiện: 2026-11-17 (Asia/Saigon)
- Repository root: `E:\University\Semester_7\HCI\BTL`
- Kết luận: **foundation web/data/tooling PASS; Blender baseline FAIL; GLB/MPFB/manual QA NOT YET TESTED**
- Local bootstrap commit: `92e2951 chore: bootstrap project foundation` (report này được thêm ở commit tiếp theo)

## 1. Task summary

Đã tạo monorepo npm workspaces, React/TypeScript/Vite shell có ba route, viewer placeholder có nhãn unverified, canonical data/schema, adaptive/3D/data contracts, read-only Blender preflight, GLB structural validator, environment doctor, tests, CI, workflow và tài liệu handoff tiếng Việt. Không tạo animation, không mở/chạy script trên model và không tạo remote.

`blender/avatar_master.blend` tồn tại trước task. File được giữ nguyên, chỉ được track như binary trong local Git. SHA-256 trước và sau đều:

```text
E15142798E8C573AA80243DE6D6F24B48CC517BBC5DD410DC1262AD1432480FA
```

## 2. System environment thực tế

| Hạng mục | Kết quả | Trạng thái |
|---|---|---|
| OS | Windows_NT 10.0.26300 x64 | PASS |
| Git | 2.45.1.windows.1 | PASS |
| Git LFS | 3.5.1 | PASS (tool có sẵn, tracking chưa bật) |
| Node.js | 24.14.1, dòng LTS được hỗ trợ | PASS |
| npm | 11.12.1 | PASS |
| System Python | `python` 3.12.10; `py` launcher báo không có interpreter | PASS cho executable, không cần cho app |
| Blender | chỉ phát hiện 5.2.4 LTS | **FAIL** so với baseline 4.5.16 |
| MPFB | chưa mở Blender/manual preflight | NOT YET TESTED |
| Existing `.blend` | 2,154,266 bytes, hash không đổi | PASS preservation |
| Git repository ban đầu | không tồn tại | Đã init local `main`; không remote |

PowerShell chặn `npm.ps1`; kiểm thử dùng `npm.cmd`. Tài liệu CMD tránh vấn đề này.

## 3. Technology versions đã pin

| Package/runtime | Version |
|---|---:|
| Node recommendation/CI | 24.22.2 LTS (`.nvmrc`) |
| npm lockfile generator | 11.12.1 |
| React / React DOM | 19.3.1 |
| React Router DOM | 7.18.5 |
| Three.js | 0.187.0 |
| Vite | 8.3.8 |
| `@vitejs/plugin-react` | 6.3.0 |
| Vitest | 5.1.0 |
| TypeScript | 5.9.3 |
| ESLint | 10.15.0 |
| typescript-eslint | 8.73.0 |
| Ajv | 8.20.0 |

Official/npm metadata checks xác nhận Vite 8 yêu cầu Node `^20.19 || >=22.12`, Vitest 5.1 hỗ trợ `^24`/`>=26`, TypeScript ESLint hỗ trợ TypeScript `<6.1` và ESLint 10, React Router chấp nhận React >=18. Node 24/26 đều là LTS tại ngày task; chọn Node 24 để khớp máy và CI.

## 4. Final repository tree

```text
.
├─ .github/workflows/ci.yml
├─ apps/web/
│  ├─ public/data/ + public/models/signs/
│  ├─ src/{app,components/viewer,features,services,types,styles}/
│  └─ tests/
├─ blender/
│  ├─ avatar_master.blend (pre-existing, unchanged)
│  ├─ master/, working/{huy-anh,mien}/
│  └─ scripts/, presets/, tests/
├─ assets/{references,staging,exports/signs,previews}/
├─ data/{signs.json,quizzes.json}
├─ schemas/{sign.schema.json,quiz.schema.json}
├─ tools/{doctor,validate-data,sync-data,validate-assets}.mjs
│  └─ tests/validate-data.test.mjs
├─ docs/
│  ├─ architecture/, contracts/, setup/, workflows/, team/
│  ├─ qa/, decisions/, reports/
│  └─ team/HANDOFF.md
├─ README.md
├─ package.json + package-lock.json
└─ shared editor/Git/env/ESLint config
```

Generated `node_modules/` và `apps/web/dist/` bị ignore.

## 5. Created/modified files

- Tạo 64 text/config/generated files và track một binary có sẵn trong initial commit; không có source project cũ khác để overwrite.
- Frontend: app shell, lesson/quiz/review routes, viewer boundary, types/service, responsive styles, two smoke tests.
- Data: six placeholder entries S001–S006, empty quizzes, two schemas, sync and policy tests.
- 3D: contract, binary policy, directories, read-only `preflight.py`, structural GLB/skeleton validator.
- Collaboration: ownership/handoff, Git and asset workflow, setup, QA, ADR, CI.
- Local Git: `main`, no remote, initial commit includes `package-lock.json`.

## 6. Architecture decisions

1. Một npm-workspace repository và một frontend app.
2. Exact dependency pins + committed lockfile + `npm ci`.
3. Một self-contained GLB/sign ở release đầu.
4. `data/` là canonical; public data được generate/checked.
5. LocalStorage + pure adaptive rules, không backend/auth/ML.
6. CI không cần Blender/MPFB; manual/educational validation tách khỏi automated checks.
7. Binary không text-merge; LFS chỉ bật khi toàn nhóm sẵn sàng.

Chi tiết tại `docs/decisions/ADR-0001-project-architecture.md`.

## 7. Actual commands executed

```text
Directory/Git/file inventories; recursive *.blend/*.glb lookup
git/node/npm/python/py/blender/git-lfs version checks
Blender executable discovery + blender --version
Get-FileHash blender/avatar_master.blend -Algorithm SHA256
npm view <selected packages> version/engines/peerDependencies
npm install --ignore-scripts
npm run sync:data
npm run check
npm run doctor (sửa lỗi npm.cmd discovery rồi chạy lại)
npm run dev --workspace @hci-sign/web -- --host 127.0.0.1 --port 4173
Invoke-WebRequest http://127.0.0.1:4173/
npm ci --ignore-scripts
npm run check
npm ci
npm run check
git init -b main
git add -A
git commit -m "chore: bootstrap project foundation"
```

Không chạy Blender với `.blend`; không chạy MPFB/preflight; không push remote.

## 8. Test results

| Check | Evidence | Result |
|---|---|---|
| `npm ci` | 145 packages, audit 147, 0 vulnerabilities | PASS |
| TypeScript | `tsc -b --pretty false` | PASS |
| ESLint | `eslint src tests --max-warnings 0` | PASS |
| Data schema/policy | 6 signs, 0 quizzes valid | PASS |
| Sync integrity | public data matches canonical | PASS |
| Data tests | 4/4: canonical, duplicate ID, invalid status, invalid approval | PASS |
| Web tests | 2/2 route/viewer smoke tests | PASS |
| Production build | Vite 8.3.8, 28 modules, JS 261.01 kB (83.10 kB gzip) | PASS |
| Dev server | ready in 190 ms; HTTP 200; expected title present | PASS |
| Asset pending handling | 0 failed, 6 pending | PASS behavior; content NOT YET TESTED |
| Blender expected 4.5.16 | doctor found 5.2.4 only | **FAIL** |
| MPFB | not inspected | NOT YET TESTED |
| GLB clip/skin/rig | no GLB exists | NOT YET TESTED |
| Browser 3D controls/manual QA | no real GLB | NOT YET TESTED |
| Expert educational verification | no content/evidence fabricated | NOT YET TESTED |
| CI remote run | no GitHub remote/workflow run | SKIPPED |

Final `npm run check` exit code: 0. `npm run doctor` exit code: 1 vì Blender mismatch có chủ đích.

## 9. Unresolved issues và risks

- Máy audit không có Blender 4.5.16 ở đường dẫn discoverable; 5.2.4 có thể save-upgrade file nên không được dùng để mở/save master candidate khi chưa thống nhất.
- MPFB version/availability, armature, finger controls, mesh relationship và Blender 4.5 Action/NLA behavior chưa kiểm tra.
- Chưa có GLB; Three.js dependency/boundary có sẵn nhưng playback/camera/lighting chưa được chứng minh.
- `avatar_master.blend` chưa được xác định là approved canonical master.
- Git LFS chưa bật; nhóm phải thống nhất trước khi asset tăng.
- Expert/reference availability có thể buộc giảm scope còn 3–4 signs tại Day 5.
- Windows sandbox cần per-command safe-directory do test runner dùng Windows account khác; user account sở hữu folder nên Git thông thường không cần workaround này.

## 10. Remaining dependencies

REQUIRED tiếp theo trên máy 3D: xác nhận/cài side-by-side Blender 4.5.16 theo quyết định nhóm, xác nhận MPFB tương thích, tạo working copy và chạy read-only preflight. REQUIRED cho mọi máy: Node 24 LTS, npm 11, Git. OPTIONAL: Git LFS sau quyết định chung; System Python không cần cho app.

## 11. Team handoff

- Huy Anh không sửa trực tiếp file candidate; tạo working copy, chạy TASK-0002 và duyệt master revision.
- Mien chờ master revision rồi làm đúng working folder/lock.
- Nhat bắt đầu từ `apps/web`, giữ viewer boundary và chỉ tích hợp GLB đúng contract.
- Thao cập nhật `data/`/evidence, chạy sync/validation, không dùng approval giả.
- Tất cả branch ngắn + PR, chạy `npm run check`; shared contract/production asset cần owner review.

Hướng dẫn chia sẻ ngắn: `docs/team/HANDOFF.md`.

## 12. Recommended next tasks

1. **TASK-0002:** Blender MPFB rig inspection và validation trên working copy; không save master bằng version sai.
2. **TASK-0003:** 3D-to-GLB export và Three.js playback smoke test với một technical fixture được dán nhãn unverified.
3. **TASK-0004:** Reusable sign animation production pipeline sau khi master/export contract đã chứng minh.

Không task nào ở trên được bắt đầu tự động trong TASK-0001.
