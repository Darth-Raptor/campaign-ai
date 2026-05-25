params [
    ["_snapshot", CAI_lastDebugSnapshot, [[]]]
];

private _groups = [_snapshot, "groups", []] call CAI_fnc_getKV;

{
    private _groupId = [_x, "groupId", "group"] call CAI_fnc_getKV;
    private _position = [_x, "position", [0, 0, 0]] call CAI_fnc_getKV;
    private _sideName = [_x, "side", "UNKNOWN"] call CAI_fnc_getKV;
    private _status = [_x, "status", "IDLE"] call CAI_fnc_getKV;
    private _orderType = [_x, "currentOrderType", _status] call CAI_fnc_getKV;
    private _targetObjectiveId = [_x, "targetObjectiveId", ""] call CAI_fnc_getKV;
    private _distanceToTarget = [_x, "distanceToTarget", -1] call CAI_fnc_getKV;
    private _movementState = [_x, "movementState", "IDLE"] call CAI_fnc_getKV;
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
    private _targetText = if (_targetObjectiveId isEqualTo "") then {"pos"} else {_targetObjectiveId};
    private _distanceText = if (_distanceToTarget >= 0) then {format [" | %1m", round _distanceToTarget]} else {""};
    _marker setMarkerText format ["CAI %1 | %2 %3 -> %4%5", _groupId, _movementState, _orderType, _targetText, _distanceText];
    CAI_debugMarkers pushBackUnique _marker;
} forEach _groups;

true
