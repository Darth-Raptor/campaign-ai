params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith { false };
if (!(_logic getVariable ["CAI_debugMarkers", true])) exitWith { false };

private _response = ["CAIPython.api.get_world_debug_markers", [[["limit", 500]]], false] call CAI_fnc_pyCall;
if (!((_response select 0) isEqualTo true)) exitWith {
    ["[CAI WORLD]", format ["World model debug marker request failed. Status: %1.", _response select 1]] call CAI_fnc_log;
    false
};

private _payloadOut = _response select 2;
private _markers = [_payloadOut, "markers", []] call CAI_fnc_getKV;
CAI_lastWorldDebugMarkers = _markers;
[_markers] call CAI_fnc_drawWorldDebugMarkers;

["[CAI WORLD]", format ["World model debug markers drawn. Count: %1.", count _markers]] call CAI_fnc_log;
true

