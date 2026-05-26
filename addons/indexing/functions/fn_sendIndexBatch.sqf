params [
    ["_indexId", "", [""]],
    ["_batchNumber", 0, [0]],
    ["_locations", [], [[]]],
    ["_terrainCells", [], [[]]],
    ["_roads", [], [[]]],
    ["_tacticalSites", [], [[]]]
];

private _payload = [
    ["indexId", _indexId],
    ["batchNumber", _batchNumber],
    ["locations", _locations],
    ["terrainCells", _terrainCells],
    ["roads", _roads],
    ["tacticalSites", _tacticalSites]
];

private _response = ["CAIPython.api.add_map_index_batch", [_payload], false] call CAI_fnc_pyCall;
if (!((_response select 0) isEqualTo true)) exitWith {
    ["[CAI INDEX]", format ["Index batch %1 failed. Status: %2.", _batchNumber, _response select 1]] call CAI_fnc_log;
    false
};

private _payloadOut = _response select 2;
["[CAI INDEX]", format [
    "Index batch %1 stored. Locations: %2. Cells: %3. Roads: %4. Sites: %5.",
    _batchNumber,
    [_payloadOut, "locationCount", count _locations] call CAI_fnc_getKV,
    [_payloadOut, "terrainCellCount", count _terrainCells] call CAI_fnc_getKV,
    [_payloadOut, "roadCount", count _roads] call CAI_fnc_getKV,
    [_payloadOut, "tacticalSiteCount", count _tacticalSites] call CAI_fnc_getKV
]] call CAI_fnc_log;

true

