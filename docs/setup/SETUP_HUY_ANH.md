# Setup Huy Anh — 3D Lead

Required: Git, Blender 5.2.4 LTS, MPFB 2.0.18, Node/npm theo repo, browser. Làm phần chung trong `docs/team/ONBOARDING.md`, cài MPFB từ release 2.0.18 qua Blender Preferences > Add-ons/Extensions và xác nhận version trong UI.

```cmd
npm ci
npm run verify:master
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --version
certutil -hashfile blender\master\avatar_master.blend SHA256
```

Huy Anh quản lý master lock, scripts/export và S001–S003. Dùng production contract để tạo working copy; không save trực tiếp master. Khi lỗi gửi branch/commit, master hash, Blender/MPFB version, command/report JSON và screenshot. Không tự sửa rig để vượt validator.
