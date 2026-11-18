# Onboarding dự án

## Bắt đầu

Windows CMD:

```cmd
git clone https://github.com/lehuyanh423015/HCI-Sign-Language.git
cd HCI-Sign-Language
git switch main
git pull --ff-only
git status --short --branch
```

Đọc `AGENTS.md`, `docs/team/MASTER_V1_HANDOFF.md`, ma trận/checklist và guide vai trò. Không hardcode ổ đĩa cá nhân trong commit.

## Web/metadata

Node version theo `.nvmrc`, npm theo `package.json`:

```cmd
node --version
npm --version
npm ci
npm run sync:data
npm run sync:technical-assets
npm run check
npm run dev
```

Mở `http://localhost:5173/technical-sign-preview`. Nếu install lỗi, gửi OS, `node --version`, `npm --version`, command đầy đủ và log; không chạy `npm audit fix --force`.

## Blender/animation

Chỉ Huy Anh/Mien cần Blender 5.2.4 LTS + MPFB 2.0.18. Kiểm tra:

```cmd
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --version
certutil -hashfile blender\master\avatar_master.blend SHA256
```

Hash phải khớp `blender/master/master-avatar.manifest.json`. Luôn tạo isolated copy bằng `create_sign_working_copy.py`; không mở master rồi Ctrl+S. Chi tiết ở production contract.

## Vấn đề thường gặp

- Sai Blender: dừng, cài đúng 5.2.4; không dùng 4.5.16.
- Hash master sai: không animate/export; giữ file và báo Huy Anh cùng `git status`/hash.
- `npm ci` báo dev audit notices: ghi lại; không force-upgrade lockfile.
- GLB không chạy: chạy Blender validator, package validator, sync, rồi browser test; không đổi metadata để che clip sai.
- Binary conflict: không merge `.blend`; chọn owner/version qua PR, giữ cả hai file nếu cần điều tra.

Repository chưa có top-level LICENSE được owner duyệt. Không tự chọn license hoặc thêm reference media có quyền sử dụng không rõ.
