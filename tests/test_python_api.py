from __future__ import annotations

import importlib.util
import json
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


def sqf_payload(**items):
    return [[key, value] for key, value in items.items()]


def from_sqf_payload(value):
    if isinstance(value, list):
        if all(isinstance(item, list) and len(item) == 2 and isinstance(item[0], str) for item in value):
            return {key: from_sqf_payload(item_value) for key, item_value in value}
        return [from_sqf_payload(item) for item in value]
    return value


class PythonApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mission_root = Path(self.temp_dir.name)
        self.output_path = self.mission_root / "campaign_ai" / "map_index.json"
        self.package = load_caipython()
        self.api = self.package.api

    def tearDown(self):
        self.temp_dir.cleanup()

    def begin_payload(self, force_reindex=False):
        return sqf_payload(
            schemaVersion=2,
            indexId="VR_TestMission",
            worldName="VR",
            missionName="TestMission",
            worldSize=8192,
            missionRoot=str(self.mission_root),
            outputPath=str(self.output_path),
            forceReindex=force_reindex,
            cellSize=500,
            roadScanRadius=350,
            objectScanRadius=300,
            debugMarkers=True,
        )

    def add_sample_batch(self):
        batch = sqf_payload(
            indexId="VR_TestMission",
            batchNumber=1,
            locations=[
                sqf_payload(
                    locationId="loc_1",
                    name="Test Village",
                    type="NameVillage",
                    category="settlement",
                    position=[100, 200, 0],
                    source="nearestLocations",
                ),
                sqf_payload(
                    locationId="loc_mount_1",
                    name="",
                    type="Mount",
                    category="terrain",
                    position=[1000, 1000, 0],
                    source="nearestLocations",
                ),
                sqf_payload(
                    locationId="loc_mount_2",
                    name="",
                    type="Mount",
                    category="terrain",
                    position=[1100, 1050, 0],
                    source="nearestLocations",
                ),
            ],
            terrainCells=[
                sqf_payload(
                    cellId="cell_250_250",
                    center=[250, 250, 0],
                    cellSize=500,
                    heightASL=10,
                    surfaceType="#GdtGrassGreen",
                    isWater=False,
                    slopeEstimate=0.05,
                    roadDensity=2,
                    structureDensity=3,
                    terrainCategory="open",
                )
            ],
            roads=[
                sqf_payload(
                    roadId="road_1000_1000",
                    position=[100, 100, 0],
                    roadInfo=["ROAD"],
                    connectedRoadIds=["road_1100_1000"],
                    source="nearRoads",
                ),
                sqf_payload(
                    roadId="road_1100_1000",
                    position=[110, 100, 0],
                    roadInfo=["ROAD"],
                    connectedRoadIds=["road_1000_1000"],
                    source="nearRoads",
                ),
            ],
            tacticalSites=[
                sqf_payload(
                    siteId="site_FUELSTATION_1000_1000",
                    type="FUELSTATION",
                    position=[100, 100, 0],
                    confidence=1,
                    source="nearestTerrainObjects",
                ),
                sqf_payload(
                    siteId="site_POWER_LINES_2000_2000",
                    type="POWER LINES",
                    position=[2000, 2000, 0],
                    confidence=1,
                    source="nearestTerrainObjects",
                ),
                sqf_payload(
                    siteId="site_POWER_LINES_2050_2050",
                    type="POWER LINES",
                    position=[2050, 2050, 0],
                    confidence=1,
                    source="nearestTerrainObjects",
                ),
                sqf_payload(
                    siteId="site_RAILWAY_3000_3000",
                    type="RAILWAY",
                    position=[3000, 3000, 0],
                    confidence=1,
                    source="nearestTerrainObjects",
                ),
                sqf_payload(
                    siteId="site_RAILWAY_3050_3050",
                    type="RAILWAY",
                    position=[3050, 3050, 0],
                    confidence=1,
                    source="nearestTerrainObjects",
                ),
            ],
        )
        return self.api.add_map_index_batch(batch)

    def world_payload(
        self,
        index_path=None,
        density="BALANCED",
        minimum_score=40,
        world_name="VR",
        world_size=8192,
        custom_objectives=None,
    ):
        return sqf_payload(
            missionRoot=str(self.mission_root),
            indexPath=str(index_path or self.output_path),
            worldName=world_name,
            worldSize=world_size,
            missionName="TestMission",
            density=density,
            minimumScore=minimum_score,
            debugMarkers=True,
            customObjectives=custom_objectives or [],
        )

    def write_world_index(self, candidates, schema_version=2, world_name="VR", world_size=8192):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schemaVersion": schema_version,
            "world": {
                "worldName": world_name,
                "worldSize": world_size,
            },
            "mission": {
                "missionName": "TestMission",
            },
            "objectiveCandidates": candidates,
            "terrainFeatureCandidates": [],
            "infrastructureCorridors": [],
            "summary": {
                "objectiveCandidateCount": len(candidates),
            },
        }
        self.output_path.write_text(json.dumps(data), encoding="utf-8")

    def candidate(self, candidate_id, score, position, source_type="NameVillage", name=None, candidate_type="settlement"):
        return {
            "candidateId": candidate_id,
            "candidateType": candidate_type,
            "sourceId": candidate_id.replace("cand_", "source_"),
            "sourceType": source_type,
            "name": candidate_id if name is None else name,
            "position": position,
            "score": score,
            "objectiveEligible": True,
            "reasons": ["test candidate"],
        }

    def custom_objective(
        self,
        custom_id,
        name,
        position,
        radius=300,
        objective_type="military",
        description="fob",
        owner="NONE",
        significance="MEDIUM",
    ):
        return sqf_payload(
            customObjectiveId=custom_id,
            name=name,
            objectiveType=objective_type,
            objectiveDescription=description,
            radius=radius,
            initialOwner=owner,
            significance=significance,
            position=position,
        )

    def test_pythia_marker_and_ping(self):
        self.assertEqual((PYTHON_CODE / "$PYTHIA$").read_text(encoding="utf-8").strip(), "CAIPython")
        success, status, payload, logs = self.api.ping()
        self.assertTrue(success)
        self.assertEqual(status, "OK")
        self.assertEqual(dict(payload)["package"], "CAIPython")
        self.assertTrue(logs)

    def test_index_lifecycle_writes_json(self):
        begin = self.api.begin_map_index(self.begin_payload())
        self.assertTrue(begin[0], begin)
        self.assertFalse(dict(begin[2])["skipScan"])

        batch = self.add_sample_batch()
        self.assertTrue(batch[0], batch)
        batch_payload = dict(batch[2])
        self.assertEqual(batch_payload["locationCount"], 3)
        self.assertEqual(batch_payload["roadCount"], 2)

        final = self.api.finalize_map_index(sqf_payload(indexId="VR_TestMission"))
        self.assertTrue(final[0], final)
        self.assertTrue(self.output_path.exists())

        data = json.loads(self.output_path.read_text(encoding="utf-8"))
        self.assertEqual(data["schemaVersion"], 2)
        self.assertEqual(data["world"]["worldName"], "VR")
        self.assertEqual(data["summary"]["locationCount"], 3)
        self.assertEqual(data["summary"]["roadNodeCount"], 2)
        self.assertEqual(data["summary"]["roadEdgeCount"], 1)
        self.assertEqual(data["summary"]["tacticalSiteCount"], 5)
        self.assertIn("objectiveCandidates", data)
        self.assertIn("terrainFeatureCandidates", data)
        self.assertIn("infrastructureCorridors", data)
        self.assertIn("dataQuality", data)

    def test_existing_index_can_skip_scan(self):
        self.assertTrue(self.api.begin_map_index(self.begin_payload())[0])
        self.assertTrue(self.add_sample_batch()[0])
        self.assertTrue(self.api.finalize_map_index(sqf_payload(indexId="VR_TestMission"))[0])

        begin = self.api.begin_map_index(self.begin_payload())
        self.assertTrue(begin[0], begin)
        payload = dict(begin[2])
        self.assertTrue(payload["skipScan"])
        self.assertEqual(dict(payload["summary"])["worldName"], "VR")

    def test_force_reindex_ignores_existing_index(self):
        self.assertTrue(self.api.begin_map_index(self.begin_payload())[0])
        self.assertTrue(self.add_sample_batch()[0])
        self.assertTrue(self.api.finalize_map_index(sqf_payload(indexId="VR_TestMission"))[0])

        begin = self.api.begin_map_index(self.begin_payload(force_reindex=True))
        self.assertTrue(begin[0], begin)
        self.assertFalse(dict(begin[2])["skipScan"])

    def test_noisy_raw_records_are_derived_not_objectives(self):
        self.assertTrue(self.api.begin_map_index(self.begin_payload())[0])
        self.assertTrue(self.add_sample_batch()[0])
        self.assertTrue(self.api.finalize_map_index(sqf_payload(indexId="VR_TestMission"))[0])

        data = json.loads(self.output_path.read_text(encoding="utf-8"))
        raw_location_types = [item["type"] for item in data["locations"]]
        raw_site_types = [item["type"] for item in data["tacticalSites"]]
        objective_source_types = [item["sourceType"] for item in data["objectiveCandidates"]]

        self.assertEqual(raw_location_types.count("Mount"), 2)
        self.assertEqual(raw_site_types.count("POWER LINES"), 2)
        self.assertNotIn("Mount", objective_source_types)
        self.assertNotIn("POWER LINES", objective_source_types)
        self.assertGreaterEqual(len(data["terrainFeatureCandidates"]), 1)
        self.assertGreaterEqual(len(data["infrastructureCorridors"]), 2)

        power_corridors = [item for item in data["infrastructureCorridors"] if item["sourceType"] == "POWER LINES"]
        railway_corridors = [item for item in data["infrastructureCorridors"] if item["sourceType"] == "RAILWAY"]
        self.assertEqual(len(power_corridors), 1)
        self.assertFalse(power_corridors[0]["objectiveEligible"])
        self.assertEqual(power_corridors[0]["sourceCount"], 2)
        self.assertEqual(len(railway_corridors), 1)
        self.assertTrue(railway_corridors[0]["objectiveEligible"])

        self.assertEqual(data["dataQuality"]["rawMountCount"], 2)
        self.assertEqual(data["dataQuality"]["rawPowerLineCount"], 2)
        self.assertEqual(data["summary"]["objectiveCandidateCount"], len(data["objectiveCandidates"]))
        self.assertEqual(data["summary"]["infrastructureCorridorCount"], len(data["infrastructureCorridors"]))

    def test_debug_marker_api_returns_top_objectives(self):
        self.assertTrue(self.api.begin_map_index(self.begin_payload())[0])
        self.assertTrue(self.add_sample_batch()[0])
        self.assertTrue(self.api.finalize_map_index(sqf_payload(indexId="VR_TestMission"))[0])

        response = self.api.get_map_index_debug_markers(
            sqf_payload(
                missionRoot=str(self.mission_root),
                outputPath=str(self.output_path),
                markerMode="OBJECTIVES",
                limit=100,
            )
        )

        self.assertTrue(response[0], response)
        payload = from_sqf_payload(response[2])
        self.assertEqual(payload["markerMode"], "OBJECTIVES")
        self.assertLessEqual(payload["markerCount"], 100)
        self.assertEqual(payload["markerCount"], len(payload["markers"]))
        self.assertTrue(payload["markers"])
        self.assertTrue(all(item["kind"] == "objective" for item in payload["markers"]))
        self.assertTrue(all(item["markerId"].startswith("CAI_IDX_OBJECTIVE_") for item in payload["markers"]))

    def test_debug_marker_api_can_include_context(self):
        self.assertTrue(self.api.begin_map_index(self.begin_payload())[0])
        self.assertTrue(self.add_sample_batch()[0])
        self.assertTrue(self.api.finalize_map_index(sqf_payload(indexId="VR_TestMission"))[0])

        response = self.api.get_map_index_debug_markers(
            sqf_payload(
                missionRoot=str(self.mission_root),
                outputPath=str(self.output_path),
                markerMode="OBJECTIVES_CONTEXT",
                limit=100,
            )
        )

        self.assertTrue(response[0], response)
        payload = from_sqf_payload(response[2])
        marker_kinds = {item["kind"] for item in payload["markers"]}
        self.assertEqual(payload["markerMode"], "OBJECTIVES_CONTEXT")
        self.assertLessEqual(payload["markerCount"], 100)
        self.assertIn("objective", marker_kinds)
        self.assertIn("terrain", marker_kinds)
        self.assertIn("corridor", marker_kinds)

    def test_output_path_must_stay_inside_mission_root(self):
        outside = self.mission_root.parent / "outside.json"
        payload = self.begin_payload()
        for item in payload:
            if item[0] == "outputPath":
                item[1] = str(outside)

        response = self.api.begin_map_index(payload)
        self.assertFalse(response[0], response)
        self.assertEqual(response[1], "VALIDATION_ERROR")

    def test_world_model_initializes_from_map_index(self):
        self.assertTrue(self.api.begin_map_index(self.begin_payload())[0])
        self.assertTrue(self.add_sample_batch()[0])
        self.assertTrue(self.api.finalize_map_index(sqf_payload(indexId="VR_TestMission"))[0])

        response = self.api.init_world_model(self.world_payload())
        self.assertTrue(response[0], response)
        summary = from_sqf_payload(response[2])
        self.assertTrue(summary["initialized"])
        self.assertEqual(summary["density"], "BALANCED")
        self.assertGreater(summary["seededObjectiveCount"], 0)

        exported = self.package.api.world_model.export_world_model()
        objectives = exported["objectives"]
        self.assertTrue(all(item["owner"] == "NONE" for item in objectives))
        self.assertTrue(all(item["initialOwner"] == "NONE" for item in objectives))
        self.assertTrue(all(item["control"] == 0 for item in objectives))
        self.assertEqual([item["objectiveId"] for item in objectives], [f"obj_seed_{index:03d}" for index in range(1, len(objectives) + 1)])

    def test_world_model_debug_markers_show_seeded_objectives(self):
        candidates = [self.candidate(f"cand_{index:03d}", 95 - index, [index * 800, index * 800, 0]) for index in range(1, 8)]
        self.write_world_index(candidates)
        self.assertTrue(self.api.init_world_model(self.world_payload())[0])

        response = self.api.get_world_debug_markers(sqf_payload(limit=100))
        self.assertTrue(response[0], response)
        payload = from_sqf_payload(response[2])
        self.assertEqual(payload["markerCount"], len(payload["markers"]))
        self.assertTrue(payload["markers"])
        self.assertTrue(all(item["kind"] == "seeded_objective" for item in payload["markers"]))
        self.assertTrue(all(item["markerId"].startswith("CAI_WORLD_OBJ_SEED_") for item in payload["markers"]))

    def test_world_model_rejects_index_outside_mission_root(self):
        outside = self.mission_root.parent / "outside_index.json"
        response = self.api.init_world_model(self.world_payload(index_path=outside))
        self.assertFalse(response[0], response)
        self.assertEqual(response[1], "VALIDATION_ERROR")

    def test_world_model_rejects_invalid_schema(self):
        self.write_world_index([self.candidate("cand_001", 80, [100, 100, 0])], schema_version=1)
        response = self.api.init_world_model(self.world_payload())
        self.assertFalse(response[0], response)
        self.assertEqual(response[1], "VALIDATION_ERROR")

    def test_world_model_uses_map_scaled_count(self):
        candidates = [
            self.candidate(f"cand_{index:03d}", 95 - (index % 25), [(index % 20) * 1600, (index // 20) * 1600, 0])
            for index in range(1, 301)
        ]
        self.write_world_index(candidates, world_size=30720)
        response = self.api.init_world_model(self.world_payload(world_size=30720, density="BALANCED"))
        self.assertTrue(response[0], response)
        summary = from_sqf_payload(response[2])
        self.assertEqual(summary["targetObjectiveCount"], 120)
        self.assertEqual(summary["seededObjectiveCount"], 120)

    def test_world_model_score_and_spread_keeps_geographic_coverage(self):
        clustered = [self.candidate(f"cluster_{index:03d}", 95 - index, [100 + index * 10, 100 + index * 10, 0]) for index in range(1, 16)]
        spread = [self.candidate(f"spread_{index:03d}", 70 - index, [2500 + index * 1000, 4000, 0]) for index in range(1, 8)]
        self.write_world_index(clustered + spread)
        response = self.api.init_world_model(self.world_payload())
        self.assertTrue(response[0], response)

        objectives = self.package.api.world_model.export_world_model()["objectives"]
        source_ids = {item["sourceCandidateId"] for item in objectives}
        self.assertTrue(any(item.startswith("spread_") for item in source_ids))

    def test_world_model_relaxes_spacing_to_reach_target(self):
        candidates = [self.candidate(f"cand_close_{index:03d}", 90 - index, [100 + index * 250, 100, 0]) for index in range(1, 20)]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload())
        self.assertTrue(response[0], response)
        summary = from_sqf_payload(response[2])
        self.assertEqual(summary["targetObjectiveCount"], 17)
        self.assertEqual(summary["seededObjectiveCount"], 17)

    def test_world_model_groups_same_kind_candidates_within_100m(self):
        candidates = [
            self.candidate("tower_a", 90, [100, 100, 0], source_type="TRANSMITTER", name="", candidate_type="communications"),
            self.candidate("tower_b", 89, [180, 100, 0], source_type="TRANSMITTER", name="", candidate_type="communications"),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload())
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        objectives = self.package.api.world_model.export_world_model()["objectives"]
        self.assertEqual(summary["groupedCandidateCount"], 1)
        self.assertEqual(summary["objectiveGroupCount"], 1)
        self.assertEqual(summary["seededObjectiveCount"], 1)
        self.assertEqual(objectives[0]["sourceType"], "TRANSMITTER")
        self.assertEqual(objectives[0]["mergedCandidateCount"], 2)
        self.assertEqual(objectives[0]["mergedCandidateIds"], ["tower_a", "tower_b"])
        self.assertEqual(objectives[0]["position"], [140.0, 100.0, 0.0])

        marker_response = self.api.get_world_debug_markers(sqf_payload(limit=10))
        marker_payload = from_sqf_payload(marker_response[2])
        self.assertTrue(marker_payload["markers"][0]["markerText"].endswith("TRANSMITTER x2"))

    def test_world_model_groups_mixed_candidates_within_200m_using_highest_score_identity(self):
        candidates = [
            self.candidate("tower_a", 90, [100, 100, 0], source_type="TRANSMITTER", name="", candidate_type="communications"),
            self.candidate("fuel_a", 70, [250, 100, 0], source_type="FUELSTATION", name="", candidate_type="logistics"),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload())
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        objective = self.package.api.world_model.export_world_model()["objectives"][0]
        self.assertEqual(summary["groupedCandidateCount"], 1)
        self.assertEqual(summary["objectiveGroupCount"], 1)
        self.assertEqual(objective["sourceCandidateId"], "tower_a")
        self.assertEqual(objective["sourceType"], "TRANSMITTER")
        self.assertEqual(objective["score"], 90)
        self.assertEqual(objective["position"], [175.0, 100.0, 0.0])
        self.assertEqual(objective["mergedSourceTypes"], ["FUELSTATION", "TRANSMITTER"])
        self.assertEqual(objective["groupingMode"], "mixed")

    def test_world_model_keeps_candidates_outside_group_thresholds_separate(self):
        candidates = [
            self.candidate("tower_a", 90, [100, 100, 0], source_type="TRANSMITTER", name="", candidate_type="communications"),
            self.candidate("fuel_a", 70, [350, 100, 0], source_type="FUELSTATION", name="", candidate_type="logistics"),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload())
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        objectives = self.package.api.world_model.export_world_model()["objectives"]
        self.assertEqual(summary["groupedCandidateCount"], 0)
        self.assertEqual(summary["objectiveGroupCount"], 0)
        self.assertEqual(summary["seededObjectiveCount"], 2)
        self.assertTrue(all("mergedCandidateCount" not in item for item in objectives))

    def test_custom_suppression_runs_before_derived_grouping(self):
        candidates = [
            self.candidate("near_custom", 95, [150, 100, 0], source_type="TRANSMITTER", name="", candidate_type="communications"),
            self.candidate("tower_a", 90, [800, 100, 0], source_type="TRANSMITTER", name="", candidate_type="communications"),
            self.candidate("tower_b", 89, [860, 100, 0], source_type="TRANSMITTER", name="", candidate_type="communications"),
        ]
        custom = [
            self.custom_objective("custom_hq", "Custom HQ", [100, 100, 0], radius=300, description="other", significance="HIGH"),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload(custom_objectives=custom))
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        objectives = self.package.api.world_model.export_world_model()["objectives"]
        self.assertEqual(summary["suppressedCandidateCount"], 1)
        self.assertEqual(summary["groupedCandidateCount"], 1)
        self.assertEqual(summary["objectiveGroupCount"], 1)
        self.assertEqual(summary["seededObjectiveCount"], 2)
        self.assertTrue(objectives[0]["isCustom"])
        self.assertNotIn("mergedCandidateCount", objectives[0])

    def test_custom_objectives_seed_before_derived_objectives(self):
        candidates = [self.candidate(f"cand_{index:03d}", 95 - index, [3000 + index * 800, 3000, 0]) for index in range(1, 8)]
        custom = [
            self.custom_objective("custom_alpha", "Alpha FOB", [100, 100, 0], owner="WEST", significance="LOW"),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload(custom_objectives=custom, minimum_score=80))
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        objectives = self.package.api.world_model.export_world_model()["objectives"]
        self.assertEqual(summary["customObjectiveCount"], 1)
        self.assertEqual(objectives[0]["objectiveId"], "obj_custom_001")
        self.assertTrue(objectives[0]["isCustom"])
        self.assertEqual(objectives[0]["sourceCandidateId"], "custom_alpha")
        self.assertTrue(all(item["score"] >= 80 for item in objectives[1:]))

    def test_custom_objectives_suppress_nearby_derived_candidates(self):
        candidates = [
            self.candidate("near_custom", 95, [150, 150, 0]),
            self.candidate("far_from_custom", 85, [3000, 3000, 0]),
        ]
        custom = [
            self.custom_objective("custom_hq", "Custom HQ", [100, 100, 0], radius=500, significance="HIGH"),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload(custom_objectives=custom))
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        objectives = self.package.api.world_model.export_world_model()["objectives"]
        source_ids = {item["sourceCandidateId"] for item in objectives}
        self.assertEqual(summary["suppressedCandidateCount"], 1)
        self.assertNotIn("near_custom", source_ids)
        self.assertIn("far_from_custom", source_ids)

    def test_custom_airfield_suppresses_nearby_support_candidates(self):
        candidates = [
            self.candidate("airfield_transmitter_1", 90, [900, 0, 0], source_type="TRANSMITTER"),
            self.candidate("airfield_transmitter_2", 89, [1400, 250, 0], source_type="TRANSMITTER"),
            self.candidate("airfield_label", 88, [1000, 400, 0], source_type="NameLocal", name="Test Airfield"),
            self.candidate("far_transmitter", 88, [2600, 0, 0], source_type="TRANSMITTER"),
            self.candidate("near_village", 86, [1200, -300, 0], source_type="NameVillage"),
            self.candidate("far_village", 87, [3600, 0, 0], source_type="NameVillage"),
        ]
        custom = [
            self.custom_objective(
                "custom_airfield",
                "Custom Airfield",
                [0, 0, 0],
                radius=300,
                description="airfield",
                significance="HIGH",
            ),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload(custom_objectives=custom, minimum_score=80))
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        objectives = self.package.api.world_model.export_world_model()["objectives"]
        source_ids = {item["sourceCandidateId"] for item in objectives}
        custom_objective = objectives[0]

        self.assertEqual(custom_objective["radius"], 300)
        self.assertEqual(custom_objective["suppressionRadius"], 2000)
        self.assertEqual(summary["suppressedCandidateCount"], 3)
        self.assertNotIn("airfield_transmitter_1", source_ids)
        self.assertNotIn("airfield_transmitter_2", source_ids)
        self.assertNotIn("airfield_label", source_ids)
        self.assertIn("far_transmitter", source_ids)
        self.assertIn("near_village", source_ids)
        self.assertIn("far_village", source_ids)

    def test_custom_objectives_reserve_slots_then_derived_fill_remaining_target(self):
        candidates = [
            self.candidate(f"cand_{index:03d}", 95 - (index % 20), [2500 + (index % 8) * 1000, 2500 + (index // 8) * 1000, 0])
            for index in range(1, 31)
        ]
        custom = [
            self.custom_objective("custom_1", "Custom One", [100, 100, 0], significance="HIGH"),
            self.custom_objective("custom_2", "Custom Two", [100, 1200, 0], significance="MEDIUM"),
        ]
        self.write_world_index(candidates)
        response = self.api.init_world_model(self.world_payload(custom_objectives=custom))
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        self.assertEqual(summary["targetObjectiveCount"], 17)
        self.assertEqual(summary["customObjectiveCount"], 2)
        self.assertEqual(summary["derivedObjectiveCount"], 15)
        self.assertEqual(summary["seededObjectiveCount"], 17)

    def test_custom_objectives_can_exceed_target_without_being_dropped(self):
        custom = [
            self.custom_objective(f"custom_{index:03d}", f"Custom {index:03d}", [index * 200, 100, 0], significance="LOW")
            for index in range(1, 16)
        ]
        self.write_world_index([], world_size=8192)
        response = self.api.init_world_model(self.world_payload(custom_objectives=custom))
        self.assertTrue(response[0], response)

        summary = from_sqf_payload(response[2])
        self.assertEqual(summary["targetObjectiveCount"], 15)
        self.assertEqual(summary["customObjectiveCount"], 15)
        self.assertEqual(summary["derivedObjectiveCount"], 0)
        self.assertEqual(summary["seededObjectiveCount"], 15)

    def test_custom_objective_fields_and_markers_are_preserved(self):
        custom = [
            self.custom_objective(
                "custom_power",
                "Power Station",
                [500, 600, 0],
                radius=750,
                objective_type="industrial",
                description="power_plant",
                owner="EAST",
                significance="HIGH",
            ),
        ]
        self.write_world_index([])
        self.assertTrue(self.api.init_world_model(self.world_payload(custom_objectives=custom))[0])

        objective = self.package.api.world_model.export_world_model()["objectives"][0]
        self.assertEqual(objective["objectiveType"], "industrial")
        self.assertEqual(objective["objectiveDescription"], "power_plant")
        self.assertEqual(objective["radius"], 750)
        self.assertEqual(objective["suppressionRadius"], 1000)
        self.assertEqual(objective["initialOwner"], "EAST")
        self.assertEqual(objective["owner"], "EAST")
        self.assertEqual(objective["control"], 100)
        self.assertEqual(objective["priority"], 95)
        self.assertTrue(objective["isCustom"])

        response = self.api.get_world_debug_markers(sqf_payload(limit=10))
        payload = from_sqf_payload(response[2])
        marker = payload["markers"][0]
        self.assertEqual(marker["kind"], "custom_objective")
        self.assertEqual(marker["markerColor"], "ColorRed")
        self.assertTrue(marker["markerText"].startswith("CAI CUSTOM 95"))


if __name__ == "__main__":
    unittest.main()
