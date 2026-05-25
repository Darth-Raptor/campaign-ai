params [
    ["_snapshot", CAI_lastDebugSnapshot, [[]]]
];

private _objectives = [_snapshot, "objectives", []] call CAI_fnc_getKV;

{
    private _objectiveId = [_x, "objectiveId", "objective"] call CAI_fnc_getKV;
    private _position = [_x, "position", [0, 0, 0]] call CAI_fnc_getKV;
    private _owner = [_x, "owner", "UNKNOWN"] call CAI_fnc_getKV;
    private _control = [_x, "control", 0] call CAI_fnc_getKV;
    private _priority = [_x, "priority", 0] call CAI_fnc_getKV;
    private _marker = format ["CAI_OBJ_%1", _objectiveId];

    deleteMarker _marker;
    createMarker [_marker, _position];
    _marker setMarkerShape "ICON";
    _marker setMarkerType "mil_flag";
    _marker setMarkerColor ([_owner] call {
        params ["_sideName"];
        if (_sideName isEqualTo "WEST") exitWith {"ColorWEST"};
        if (_sideName isEqualTo "EAST") exitWith {"ColorEAST"};
        if (_sideName isEqualTo "GUER") exitWith {"ColorGUER"};
        "ColorUNKNOWN"
    });
    _marker setMarkerText format ["CAI OBJ %1 | %2 | P%3", _objectiveId, _control, _priority];
    CAI_debugMarkers pushBackUnique _marker;
} forEach _objectives;

true

