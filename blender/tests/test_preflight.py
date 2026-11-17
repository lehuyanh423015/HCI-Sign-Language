"""Blender-side tests for the read-only rig preflight."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
import unittest
from pathlib import Path

import bpy


def script_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect-rig", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


ARGS = script_arguments()
RIG_SCRIPT = Path(ARGS.inspect_rig).resolve()
SPEC = importlib.util.spec_from_file_location("hci_inspect_rig", RIG_SCRIPT)
RIG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RIG)


class PreflightTests(unittest.TestCase):
    def test_status_vocabulary(self):
        self.assertEqual(RIG.VALID_STATUSES, {"PASS", "FAIL", "SKIPPED", "NOT YET TESTED"})

    def test_side_parser_is_conservative(self):
        self.assertEqual(RIG.side_of("wrist.L"), "left")
        self.assertEqual(RIG.side_of("wrist_R"), "right")
        self.assertIsNone(RIG.side_of("bright_control"))

    def test_loaded_file_has_real_rig_inventory(self):
        report = RIG.build_report()
        self.assertTrue(bpy.data.filepath)
        self.assertGreaterEqual(len(report["armatures"]), 1)
        self.assertGreaterEqual(len(report["meshes"]), 1)
        self.assertTrue(any(row["id"] == "read_only_state" and row["status"] == "PASS" for row in report["checks"]))
        json.dumps(report)

    def test_script_contains_no_blender_save_or_animation_creation_calls(self):
        tree = ast.parse(RIG_SCRIPT.read_text(encoding="utf-8"))
        forbidden = {"save_as_mainfile", "save_mainfile", "keyframe_insert", "keyframe_delete", "action_new", "nla_tracks_new"}
        called_attributes = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        self.assertTrue(forbidden.isdisjoint(called_attributes), "Found forbidden mutating call(s): %s" % sorted(forbidden & called_attributes))


if __name__ == "__main__":
    result = unittest.main(argv=[sys.argv[0]], exit=False, verbosity=2).result
    if not result.wasSuccessful():
        raise RuntimeError("Blender preflight tests failed")
