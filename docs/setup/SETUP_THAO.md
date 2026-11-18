# Setup Thao — Content, Adaptive và QA

Required: Git và browser. Node/npm cần khi trực tiếp sửa/validate metadata; Blender/MPFB không cần mặc định.

```cmd
git status --short --branch
npm ci
npm run validate:data
npm run validate:sign-packages
```

Thao ghi source, author/date/URL/media, quyền sử dụng, variant/gloss đã xác lập, observations và evidence vào workspace Snnn. Không invent content, không coi technical fixture là sign, không đặt `APPROVED` nếu thiếu qualified linguistic review. Mở technical preview để điều phối QA, nhưng automated/browser `PASS` không phải linguistic `PASS`. Khi lỗi gửi sign ID, schema path, validation output và reference/evidence có thể truy vết; tránh commit dữ liệu nhạy cảm.
