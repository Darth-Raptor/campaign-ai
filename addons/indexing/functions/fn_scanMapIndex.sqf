params [
    ["_logic", objNull, [objNull]]
];

if (!isServer) exitWith { CAI_mapIndexingActive = false; false };

if (isMultiplayer) exitWith {
    CAI_mapIndexingActive = false;
    ["[CAI INDEX]", "Map Indexer is intended for single-player/editor-preview indexing in this branch."] call CAI_fnc_log;
    false
};

waitUntil {
    sleep 0.2;
    !isNull player || {time > 10}
};

if (isNull player) exitWith {
    CAI_mapIndexingActive = false;
    ["[CAI INDEX]", "Map Indexer requires one player unit in the mission."] call CAI_fnc_log;
    false
};

if (!CAI_systemsEnabled) exitWith {
    CAI_mapIndexingActive = false;
    ["[CAI INDEX]", format ["Map indexing skipped because Campaign AI is disabled. Reason: %1", CAI_failureReason]] call CAI_fnc_log;
    false
};

private _cellSize = (_logic getVariable ["CAI_cellSize", 500]) max 100;
private _roadScanRadius = (_logic getVariable ["CAI_roadScanRadius", 350]) max 50;
private _objectScanRadius = (_logic getVariable ["CAI_objectScanRadius", 300]) max 50;
private _outputFile = _logic getVariable ["CAI_outputFile", "campaign_ai\map_index.json"];
private _forceReindex = _logic getVariable ["CAI_forceReindex", false];
private _debugMarkers = _logic getVariable ["CAI_debugMarkers", true];
private _debugMarkerMode = _logic getVariable ["CAI_debugMarkerMode", "OBJECTIVES"];
private _missionRoot = getMissionPath "";
private _outputPath = getMissionPath _outputFile;
private _worldSize = worldSize;
private _indexId = format ["%1_%2", worldName, missionName];

private _settings = [
    ["schemaVersion", 2],
    ["indexId", _indexId],
    ["worldName", worldName],
    ["missionName", missionName],
    ["worldSize", _worldSize],
    ["missionRoot", _missionRoot],
    ["outputPath", _outputPath],
    ["forceReindex", _forceReindex],
    ["cellSize", _cellSize],
    ["roadScanRadius", _roadScanRadius],
    ["objectScanRadius", _objectScanRadius],
    ["debugMarkers", _debugMarkers],
    ["debugMarkerMode", _debugMarkerMode],
    ["startedAt", [] call CAI_fnc_getTime]
];

["[CAI INDEX]", format ["Map indexing starting for %1. Output: %2", worldName, _outputPath]] call CAI_fnc_log;

private _beginResponse = ["CAIPython.api.begin_map_index", [_settings], false] call CAI_fnc_pyCall;
if (!((_beginResponse select 0) isEqualTo true)) exitWith {
    CAI_mapIndexingActive = false;
    ["[CAI INDEX]", format ["Map index begin failed. Status: %1.", _beginResponse select 1]] call CAI_fnc_log;
    false
};

private _beginPayload = _beginResponse select 2;
private _skipScan = [_beginPayload, "skipScan", false] call CAI_fnc_getKV;
if (_skipScan) exitWith {
    CAI_lastMapIndexSummary = [_beginPayload, "summary", []] call CAI_fnc_getKV;
    CAI_mapIndexingActive = false;
    ["[CAI INDEX]", "Existing compatible map index found. Scan skipped."] call CAI_fnc_log;
    [_logic, _indexId, _missionRoot, _outputPath] call CAI_fnc_showMapIndexDebug;
    true
};

private _locations = [] call CAI_fnc_collectMapLocations;
[_indexId, 0, _locations, [], [], []] call CAI_fnc_sendIndexBatch;

private _batchNumber = 1;
private _cellCount = 0;
private _batchCells = [];
private _batchRoads = [];
private _batchSites = [];
private _halfCell = _cellSize / 2;

for "_xPos" from _halfCell to _worldSize step _cellSize do {
    for "_yPos" from _halfCell to _worldSize step _cellSize do {
        private _center = [_xPos, _yPos, 0];
        private _batch = [_center, _cellSize, _roadScanRadius, _objectScanRadius] call CAI_fnc_collectIndexBatch;

        _batchCells pushBack ([_batch, "terrainCell", []] call CAI_fnc_getKV);
        _batchRoads append ([_batch, "roads", []] call CAI_fnc_getKV);
        _batchSites append ([_batch, "tacticalSites", []] call CAI_fnc_getKV);
        _cellCount = _cellCount + 1;

        if (_debugMarkers) then {
            [_center, _cellCount, _worldSize, _cellSize] call CAI_fnc_drawIndexProgress;
        };

        if ((count _batchCells) >= 20) then {
            [_indexId, _batchNumber, [], _batchCells, _batchRoads, _batchSites] call CAI_fnc_sendIndexBatch;
            _batchNumber = _batchNumber + 1;
            _batchCells = [];
            _batchRoads = [];
            _batchSites = [];
            sleep 0.05;
        };
    };
};

if ((count _batchCells) > 0 || {(count _batchRoads) > 0} || {(count _batchSites) > 0}) then {
    [_indexId, _batchNumber, [], _batchCells, _batchRoads, _batchSites] call CAI_fnc_sendIndexBatch;
};

private _finalResponse = ["CAIPython.api.finalize_map_index", [[["indexId", _indexId], ["finishedAt", [] call CAI_fnc_getTime]]], false] call CAI_fnc_pyCall;
if ((_finalResponse select 0) isEqualTo true) then {
    CAI_lastMapIndexSummary = [_finalResponse select 2, "summary", []] call CAI_fnc_getKV;
    ["[CAI INDEX]", format ["Map indexing completed. Summary: %1", CAI_lastMapIndexSummary]] call CAI_fnc_log;
    [_logic, _indexId, _missionRoot, _outputPath] call CAI_fnc_showMapIndexDebug;
} else {
    ["[CAI INDEX]", format ["Map index finalize failed. Status: %1.", _finalResponse select 1]] call CAI_fnc_log;
};

CAI_mapIndexingActive = false;
(_finalResponse select 0)
