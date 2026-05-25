params [
    ["_snapshot", CAI_lastDebugSnapshot, [[]]]
];

private _groups = [_snapshot, "groups", []] call CAI_fnc_getKV;

{
    private _groupId = [_x, "groupId", "group"] call CAI_fnc_getKV;
    private _position = [_x, "position", [0, 0, 0]] call CAI_fnc_getKV;
    private _sideName = [_x, "side", "UNKNOWN"] call CAI_fnc_getKV;
    private _status = [_x, "status", "IDLE"] call CAI_fnc_getKV;
    private _marker = format ["CAI_GRP_%1", _groupId];

    deleteMarker _marker;
    createMarker [_marker, _position];
    _marker setMarkerShape "ICON";
    _marker setMarkerType "mil_dot";
    _marker setMarkerColor ([_sideName] call {
        params ["_sideValue"];
        if (_sideValue isEqualTo "WEST") exitWith {"ColorWEST"};
        if (_sideValue isEqualTo "EAST") exitWith {"ColorEAST"};
        if (_sideValue isEqualTo "GUER") exitWith {"ColorGUER"};
        "ColorUNKNOWN"
    });
    _marker setMarkerText format ["CAI %1 | %2", _groupId, _status];
    CAI_debugMarkers pushBackUnique _marker;
} forEach _groups;

true

