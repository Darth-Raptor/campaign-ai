params [
    ["_logic", objNull, [objNull]],
    ["_indexId", "", [""]],
    ["_missionRoot", "", [""]],
    ["_outputPath", "", [""]]
];

if (!isServer || {isNull _logic}) exitWith { false };
if (!(_logic getVariable ["CAI_debugMarkers", true])) exitWith { false };

private _markerMode = _logic getVariable ["CAI_debugMarkerMode", "OBJECTIVES"];
private _payload = [
    ["indexId", _indexId],
    ["missionRoot", _missionRoot],
    ["outputPath", _outputPath],
    ["markerMode", _markerMode],
    ["limit", 100]
];

private _response = ["CAIPython.api.get_map_index_debug_markers", [_payload], false] call CAI_fnc_pyCall;
if (!((_response select 0) isEqualTo true)) exitWith {
    ["[CAI INDEX]", format ["Map index debug marker request failed. Status: %1.", _response select 1]] call CAI_fnc_log;
    false
};

private _payloadOut = _response select 2;
private _markers = [_payloadOut, "markers", []] call CAI_fnc_getKV;
CAI_lastIndexDebugMarkers = _markers;
[_markers] call CAI_fnc_drawIndexDebugMarkers;

["[CAI INDEX]", format [
    "Map index debug markers drawn. Mode: %1. Count: %2.",
    [_payloadOut, "markerMode", _markerMode] call CAI_fnc_getKV,
    count _markers
]] call CAI_fnc_log;

true

