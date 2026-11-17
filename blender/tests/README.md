# Blender tests

`test_preflight.py` chạy bên trong Blender trên **working/temporary copy**. Test xác nhận status vocabulary, conservative side mapping, inventory thật có mesh/armature, JSON serializable và source inspector không chứa Blender save/keyframe calls.

Không chạy test trực tiếp trên master source. Dùng command trong `docs/setup/SETUP_BLENDER.md` và luôn có `--python-exit-code`.
