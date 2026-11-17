"""Read-only Blender and MPFB environment inspection.

Compatible with Blender 4.5's Python API. Invoke with --python-exit-code so a
critical RuntimeError becomes a nonzero process result. The script never
installs/enables an extension and never saves a .blend file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

try:
    import tomllib
except ImportError:  # pragma: no cover - Blender 4.5 includes tomllib
    tomllib = None


VALID_STATUSES = {"PASS", "FAIL", "SKIPPED", "NOT YET TESTED"}


def script_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect Blender and MPFB without changing preferences.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--expected-version", default="4.5.16", help="Exact project Blender baseline.")
    parser.add_argument("--require-mpfb", action="store_true", help="Treat missing/inactive MPFB as critical.")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def check(check_id: str, status: str, summary: str, critical: bool = False, details=None) -> dict:
    if status not in VALID_STATUSES:
        raise ValueError("Invalid preflight status: %s" % status)
    return {
        "id": check_id,
        "status": status,
        "summary": summary,
        "critical": critical,
        "details": details,
    }


def extension_repositories() -> list[dict]:
    repositories = []
    extensions = getattr(bpy.context.preferences, "extensions", None)
    for repository in getattr(extensions, "repos", []) if extensions else []:
        repositories.append(
            {
                "name": getattr(repository, "name", None),
                "module": getattr(repository, "module", None),
                "directory": getattr(repository, "directory", None),
                "enabled": getattr(repository, "enabled", None),
                "use_remote_url": getattr(repository, "use_remote_url", None),
            }
        )
    return repositories


def read_manifest(manifest_path: Path) -> dict:
    if not manifest_path.is_file() or tomllib is None:
        return {}
    with manifest_path.open("rb") as stream:
        data = tomllib.load(stream)
    keys = (
        "schema_version",
        "id",
        "version",
        "name",
        "type",
        "maintainer",
        "website",
        "blender_version_min",
        "blender_version_max",
        "wheels",
        "permissions",
    )
    return {key: data.get(key) for key in keys if key in data}


def discover_mpfb(activated_addons: list[str], repositories: list[dict]) -> dict:
    activated_modules = [name for name in activated_addons if "mpfb" in name.lower()]
    manifest_candidates = []
    module_files = []

    for module_name in activated_modules:
        module = sys.modules.get(module_name)
        module_file = getattr(module, "__file__", None)
        if module_file:
            module_path = Path(module_file).resolve()
            module_files.append(str(module_path))
            manifest_candidates.append(module_path.parent / "blender_manifest.toml")

    for repository in repositories:
        directory = repository.get("directory")
        if directory:
            manifest_candidates.append(Path(directory) / "mpfb" / "blender_manifest.toml")

    manifests = []
    seen = set()
    for candidate in manifest_candidates:
        normalized = str(candidate.resolve()) if candidate.exists() else str(candidate)
        if normalized in seen or not candidate.is_file():
            continue
        seen.add(normalized)
        manifests.append({"path": normalized, "metadata": read_manifest(candidate)})

    return {
        "activated_modules": activated_modules,
        "runtime_loaded": [name for name in activated_modules if name in sys.modules],
        "module_files": module_files,
        "manifests": manifests,
    }


def build_report(expected_version: str, require_mpfb: bool) -> dict:
    activated_addons = sorted(addon.module for addon in bpy.context.preferences.addons)
    repositories = extension_repositories()
    mpfb = discover_mpfb(activated_addons, repositories)
    checks = [
        check("background_mode", "PASS" if bpy.app.background else "FAIL", "Blender is running in background mode." if bpy.app.background else "Blender is not running in background mode.", True),
        check("python_api", "PASS", "bpy imported and the embedded Python API is accessible.", True, {"python": sys.version}),
    ]

    version_matches = bpy.app.version_string.startswith(expected_version)
    checks.append(
        check(
            "blender_baseline",
            "PASS" if version_matches else "FAIL",
            "Blender version matches project baseline %s." % expected_version if version_matches else "Blender %s does not match project baseline %s." % (bpy.app.version_string, expected_version),
            True,
        )
    )

    installed = bool(mpfb["manifests"] or mpfb["module_files"])
    active = bool(mpfb["activated_modules"])
    loaded = bool(mpfb["runtime_loaded"])
    checks.extend(
        [
            check("mpfb_installed", "PASS" if installed else "FAIL", "MPFB extension files and manifest were found." if installed else "MPFB extension files were not found for this Blender profile.", require_mpfb, mpfb["manifests"]),
            check("mpfb_activated", "PASS" if active else "FAIL", "MPFB is enabled in this Blender profile." if active else "MPFB is not enabled in this Blender profile.", require_mpfb, mpfb["activated_modules"]),
            check("mpfb_runtime", "PASS" if loaded else "FAIL", "MPFB initialized in the background process." if loaded else "MPFB was not loaded in the background process.", require_mpfb, mpfb["runtime_loaded"]),
        ]
    )

    return {
        "schema_version": 1,
        "inspection": "blender_environment",
        "read_only": True,
        "overall_status": "FAIL" if any(row["status"] == "FAIL" for row in checks) else "PASS",
        "blender": {
            "version": bpy.app.version_string,
            "version_tuple": list(bpy.app.version),
            "binary_path": bpy.app.binary_path,
            "background": bpy.app.background,
            "build_hash": bpy.app.build_hash.decode("utf8") if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash),
            "python": sys.version,
            "user_config": bpy.utils.user_resource("CONFIG"),
            "user_scripts": bpy.utils.user_resource("SCRIPTS"),
            "script_paths": bpy.utils.script_paths(),
        },
        "extension_repositories": repositories,
        "mpfb": mpfb,
        "checks": checks,
    }


def emit_report(report: dict, output_path: str | None) -> None:
    for row in report["checks"]:
        print("[%s] %s: %s" % (row["status"], row["id"], row["summary"]))
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    if output_path:
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialized + "\n", encoding="utf-8")
        print("JSON report: %s" % target)
    print("HCI_ENVIRONMENT_JSON_BEGIN")
    print(serialized)
    print("HCI_ENVIRONMENT_JSON_END")


def main() -> None:
    args = script_arguments()
    report = build_report(args.expected_version, args.require_mpfb)
    emit_report(report, args.output)
    critical_failures = [row["id"] for row in report["checks"] if row["critical"] and row["status"] == "FAIL"]
    if critical_failures:
        raise RuntimeError("Critical environment preflight failures: %s" % ", ".join(critical_failures))


if __name__ == "__main__":
    main()
