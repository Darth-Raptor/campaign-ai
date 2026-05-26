params [
    ["_center", [0, 0, 0], [[]]],
    ["_cellSize", 500, [0]],
    ["_roadScanRadius", 350, [0]],
    ["_objectScanRadius", 300, [0]]
];

[
    ["terrainCell", [_center, _cellSize, _roadScanRadius, _objectScanRadius] call CAI_fnc_collectTerrainCell],
    ["roads", [_center, _roadScanRadius] call CAI_fnc_collectRoadsAtPosition],
    ["tacticalSites", [_center, _objectScanRadius] call CAI_fnc_collectTacticalSitesAtPosition]
]

