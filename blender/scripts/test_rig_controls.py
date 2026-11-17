"""Controlled transient pose tests for the MPFB deformation rig."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import FINGER_CHAINS, control_test, establish_neutral_pose, require_rig, sha256


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def main():
    args = arguments()
    armature, mesh = require_rig()
    original_object_matrix = [list(row) for row in armature.matrix_world]
    results = []
    for finger_name, chain in FINGER_CHAINS.items():
        result = control_test(armature, mesh, chain[0], chain)
        result["semantic"] = finger_name
        results.append(result)

    results.append(control_test(armature, mesh, "wrist.R", FINGER_CHAINS["middle"], 8.0))
    results[-1]["semantic"] = "wrist"
    results.append(control_test(armature, mesh, "lowerarm01.R", ["wrist.R"], 8.0))
    results[-1]["semantic"] = "elbow_or_forearm"
    establish_neutral_pose(armature)

    report = {
        "schema_version": 1,
        "inspection": "controlled_rig_movement",
        "source_file": bpy.data.filepath,
        "source_sha256": sha256(bpy.data.filepath),
        "blender_version": bpy.app.version_string,
        "technical_fixture_only": True,
        "armature_object_matrix_preserved": original_object_matrix == [list(row) for row in armature.matrix_world],
        "tests": results,
        "automated_deformation_status": "PASS" if all(row["status"] == "PASS" for row in results) else "FAIL",
        "human_visual_status": "NOT YET TESTED",
        "notes": "Mesh vertex deltas prove localized deformation and exact reset; visual clipping/anatomical quality still requires preview review.",
    }
    target = Path(args.output).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in results:
        print("[%s] %s via local %s%+d: %d mesh vertices moved; max %.6f m" % (
            row["status"], row["semantic"], row["axis"]["axis"], row["axis"]["sign"],
            row["mesh_delta"]["moved_vertices"], row["mesh_delta"]["max_distance"],
        ))
    print("JSON report: %s" % target)
    if report["automated_deformation_status"] != "PASS" or not report["armature_object_matrix_preserved"]:
        raise RuntimeError("Controlled rig movement test failed")


if __name__ == "__main__":
    main()
