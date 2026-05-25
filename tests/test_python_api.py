from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_CODE = REPO_ROOT / "python_code"


def load_caipython():
    for name in list(sys.modules):
        if name == "CAIPython" or name.startswith("CAIPython."):
            del sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        "CAIPython",
        PYTHON_CODE / "__init__.py",
        submodule_search_locations=[str(PYTHON_CODE)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["CAIPython"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sample_payload():
    return [
        ["campaignId", "test_campaign"],
        ["worldName", "VR"],
        ["missionName", "Campaign AI Test"],
        [
            "objectives",
            [
                [
                    ["objectiveId", "obj_red"],
                    ["name", "Red Base"],
                    ["owner", "EAST"],
                    ["priority", 80],
                    ["position", [0, 0, 0]],
                    ["terrainType", "urban"],
                ],
                [
                    ["objectiveId", "obj_blue"],
                    ["name", "Blue Base"],
                    ["owner", "WEST"],
                    ["priority", 70],
                    ["position", [1000, 0, 0]],
                    ["terrainType", "mixed"],
                ],
            ],
        ],
        [
            "commanders",
            [
                [
                    ["commanderId", "red_cmd_01"],
                    ["side", "EAST"],
                    ["hqPosition", [0, 0, 0]],
                    ["cycleTime", 120],
                    ["reservePercentage", 0],
                ]
            ],
        ],
        [
            "virtualGroups",
            [
                [
                    ["groupId", "grp_red_001"],
                    ["side", "EAST"],
                    ["commanderId", "red_cmd_01"],
                    ["forceSize", "platoon"],
                    ["unitType", "infantry"],
                    ["mobility", "foot"],
                    ["position", [0, 0, 0]],
                    ["initialObjective", "obj_red"],
                ],
                [
                    ["groupId", "grp_blue_001"],
                    ["side", "WEST"],
                    ["commanderId", "blue_cmd_01"],
                    ["forceSize", "platoon"],
                    ["unitType", "infantry"],
                    ["mobility", "foot"],
                    ["position", [1000, 0, 0]],
                    ["initialObjective", "obj_blue"],
                ],
            ],
        ],
        ["settings", [["debugEnabled", True]]],
    ]


class PythonApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["CAI_SAVE_DIR"] = self.temp_dir.name
        self.package = load_caipython()
        self.api = self.package.api

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ping_uses_standard_envelope(self):
        success, status, payload, logs = self.api.ping()
        self.assertTrue(success)
        self.assertEqual(status, "OK")
        self.assertTrue(any(item[0] == "package" and item[1] == "CAIPython" for item in payload))
        self.assertTrue(logs)

    def test_init_save_load_and_summary(self):
        response = self.api.init_state(sample_payload())
        self.assertTrue(response[0], response)

        save_response = self.api.save_snapshot([["campaignId", "test_campaign"], ["saveName", "unit"]])
        self.assertTrue(save_response[0], save_response)

        load_response = self.api.load_snapshot([["campaignId", "test_campaign"], ["saveName", "unit"]])
        self.assertTrue(load_response[0], load_response)

        summary_response = self.api.get_state_summary()
        self.assertTrue(summary_response[0], summary_response)
        summary = dict(summary_response[2])
        self.assertEqual(summary["objectiveCount"], 2)
        self.assertEqual(summary["virtualGroupCount"], 2)

    def test_commander_cycle_returns_valid_orders_and_debug_snapshot(self):
        self.assertTrue(self.api.init_state(sample_payload())[0])

        response = self.api.commander_cycle(
            [["commanderId", "red_cmd_01"], ["gameTime", 120], ["observedEvents", []]]
        )
        self.assertTrue(response[0], response)
        payload = dict(response[2])
        self.assertIn("orders", payload)
        self.assertGreaterEqual(len(payload["orders"]), 1)

        debug_response = self.api.get_debug_snapshot([["debugMode", "BOTH"], ["gameTime", 120]])
        self.assertTrue(debug_response[0], debug_response)
        debug_payload = dict(debug_response[2])
        self.assertEqual(len(debug_payload["objectives"]), 2)

    def test_combat_resolution_updates_state(self):
        self.assertTrue(self.api.init_state(sample_payload())[0])

        response = self.api.resolve_combat_batch(
            [
                ["gameTime", 240],
                [
                    "engagements",
                    [
                        [
                            ["attackerGroupId", "grp_red_001"],
                            ["defenderGroupId", "grp_blue_001"],
                            ["objectiveId", "obj_blue"],
                            ["playersNearby", False],
                        ]
                    ],
                ],
                ["autoDetect", False],
                ["randomness", "LOW"],
            ]
        )
        self.assertTrue(response[0], response)
        payload = dict(response[2])
        self.assertEqual(len(payload["results"]), 1)


if __name__ == "__main__":
    unittest.main()

