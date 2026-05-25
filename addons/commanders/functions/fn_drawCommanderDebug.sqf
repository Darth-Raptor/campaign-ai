params [
    ["_snapshot", CAI_lastDebugSnapshot, [[]]]
];

{
    deleteMarker _x;
} forEach CAI_debugMarkers;
CAI_debugMarkers = [];

[_snapshot] call CAI_fnc_drawObjectiveDebug;
[_snapshot] call CAI_fnc_drawVirtualDebug;
[_snapshot] call CAI_fnc_drawKnowledgeDebug;

private _commanders = [_snapshot, "commanders", []] call CAI_fnc_getKV;
{
    private _commanderId = [_x, "commanderId", "cmd"] call CAI_fnc_getKV;
    private _position = [_x, "hqPosition", [0, 0, 0]] call CAI_fnc_getKV;
    private _posture = [_x, "posture", "BALANCED"] call CAI_fnc_getKV;
    private _marker = format ["CAI_CMD_%1", _commanderId];

    deleteMarker _marker;
    createMarker [_marker, _position];
    _marker setMarkerShape "ICON";
    _marker setMarkerType "mil_flag";
    _marker setMarkerColor "ColorYellow";
    _marker setMarkerText format ["CAI CMD %1 | %2", _commanderId, _posture];
    CAI_debugMarkers pushBackUnique _marker;
} forEach _commanders;

true
