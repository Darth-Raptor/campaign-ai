params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith {
    CAI_worldModelActive = false;
    false
};

waitUntil {
    sleep 0.2;
    !(isNil "CAI_systemsEnabled")
};

if (!CAI_systemsEnabled) exitWith {
    CAI_worldModelActive = false;
    ["[CAI WORLD]", format ["World model skipped because Campaign AI is disabled. Reason: %1", CAI_failureReason]] call CAI_fnc_log;
    false
};

waitUntil {
    sleep 0.5;
    isNil "CAI_mapIndexingActive" || {!CAI_mapIndexingActive}
};

private _indexFile = _logic getVariable ["CAI_mapIndexFile", "campaign_ai\map_index.json"];
private _density = _logic getVariable ["CAI_objectiveDensity", "BALANCED"];
private _minimumScoreRaw = _logic getVariable ["CAI_minimumScore", 40];
private _minimumScoreValue = if (_minimumScoreRaw isEqualType 0) then {
    _minimumScoreRaw
} else {
    private _minimumScoreText = if (_minimumScoreRaw isEqualType "") then {_minimumScoreRaw} else {str _minimumScoreRaw};
    parseNumber _minimumScoreText
};
if (_minimumScoreValue <= 1) then { _minimumScoreValue = _minimumScoreValue * 100; };
private _minimumScore = (_minimumScoreValue max 0) min 100;
private _debugMarkers = _logic getVariable ["CAI_debugMarkers", true];
private _missionRoot = getMissionPath "";
private _indexPath = getMissionPath _indexFile;

private _payload = [
    ["missionRoot", _missionRoot],
    ["indexPath", _indexPath],
    ["worldName", worldName],
    ["worldSize", worldSize],
    ["missionName", missionName],
    ["density", _density],
    ["minimumScore", _minimumScore],
    ["debugMarkers", _debugMarkers]
];

["[CAI WORLD]", format ["Runtime world model starting. Index: %1. Density: %2. Minimum score: %3.", _indexPath, _density, _minimumScore]] call CAI_fnc_log;

private _response = ["CAIPython.api.init_world_model", [_payload], false] call CAI_fnc_pyCall;
if (!((_response select 0) isEqualTo true)) exitWith {
    CAI_worldModelActive = false;
    ["[CAI WORLD]", format ["World model initialization failed. Status: %1.", _response select 1]] call CAI_fnc_log;
    false
};

CAI_lastWorldModelSummary = _response select 2;

private _sourceCount = [CAI_lastWorldModelSummary, "sourceCandidateCount", 0] call CAI_fnc_getKV;
private _eligibleCount = [CAI_lastWorldModelSummary, "eligibleCandidateCount", 0] call CAI_fnc_getKV;
private _seededCount = [CAI_lastWorldModelSummary, "seededObjectiveCount", 0] call CAI_fnc_getKV;
private _summaryDensity = [CAI_lastWorldModelSummary, "density", _density] call CAI_fnc_getKV;

["[CAI WORLD]", format [
    "Runtime world model initialized. Candidates: %1. Eligible: %2. Seeded objectives: %3. Density: %4.",
    _sourceCount,
    _eligibleCount,
    _seededCount,
    _summaryDensity
]] call CAI_fnc_log;

if (_debugMarkers) then {
    [_logic] call CAI_fnc_showWorldDebug;
};

CAI_worldModelActive = false;
true
