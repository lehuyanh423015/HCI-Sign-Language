# Setup Mien — 3D Animator

Required: Git, Blender 5.2.4 LTS, MPFB 2.0.18, browser; Node/npm là optional nhưng hữu ích để validate package. Làm onboarding chung, cài MPFB qua Blender Preferences và xác nhận đúng 2.0.18.

```cmd
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --version
certutil -hashfile blender\master\avatar_master.blend SHA256
git switch -c feat/sign-S004
```

Mien nhận S004–S006, tạo riêng từng working copy bằng script trong production contract. Không rename/reparent bone, đổi rest pose, Morph Target hoặc ghi vào `blender/master/`. Gửi `.blend`, GLB, front/side preview, JSON validation và reference status. Khi lỗi báo exact file/hash/command; không merge hai `.blend`.
