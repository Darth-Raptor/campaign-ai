params [
    ["_orders", [], [[]]],
    ["_gameTime", 0, [0]]
];

private _allowedTypes = ["DEFEND", "PATROL", "RESERVE", "ATTACK", "REINFORCE"];
private _accepted = [];
private _rejected = [];

{
    private _orderId = [_x, "orderId", ""] call CAI_fnc_getKV;
    private _groupId = [_x, "groupId", ""] call CAI_fnc_getKV;
    private _orderType = [_x, "orderType", ""] call CAI_fnc_getKV;
    private _targetObjectiveId = [_x, "targetObjectiveId", ""] call CAI_fnc_getKV;
    private _expiresAt = [_x, "expiresAt", 0] call CAI_fnc_getKV;
    private _reason = "";

    if (_groupId isEqualTo "") then { _reason = "Missing group id"; };
    if (_reason isEqualTo "" && {!(_orderType in _allowedTypes)}) then { _reason = "Order type is not allowlisted"; };
    if (_reason isEqualTo "" && {_expiresAt > 0 && {_expiresAt < _gameTime}}) then { _reason = "Order has expired"; };
    if (_reason isEqualTo "" && {!(CAI_virtualGroupMirror getOrDefault [_groupId, []] isNotEqualTo [])}) then { _reason = "Group does not exist in SQF mirror"; };
    if (_reason isEqualTo "" && {!(_targetObjectiveId isEqualTo "") && {!(CAI_objectiveMirror getOrDefault [_targetObjectiveId, []] isNotEqualTo [])}}) then { _reason = "Objective does not exist in SQF mirror"; };

    if (_reason isEqualTo "") then {
        private _group = CAI_virtualGroupMirror get _groupId;
        private _manualOverride = [_group, "manualOverride", false] call CAI_fnc_getKV;
        if (_manualOverride) then { _reason = "Group is under manual override"; };
    };

    if (_reason isEqualTo "") then {
        _accepted pushBack _x;
    } else {
        _rejected pushBack [_x, _reason];
        ["[CAI CMD]", format ["Rejected order %1. Reason: %2.", _orderId, _reason]] call CAI_fnc_log;
    };
} forEach _orders;

[_accepted, _rejected]

