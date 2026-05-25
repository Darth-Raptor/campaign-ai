params [
    ["_orders", [], [[]]]
];

{
    private _groupId = [_x, "groupId", ""] call CAI_fnc_getKV;
    if (!(_groupId isEqualTo "") && {CAI_virtualGroupMirror getOrDefault [_groupId, []] isNotEqualTo []}) then {
        private _group = CAI_virtualGroupMirror get _groupId;
        private _map = [_group] call CAI_fnc_toHashMap;
        _map set ["assignedOrder", _x];
        _map set ["status", [_x, "orderType", "ORDERED"] call CAI_fnc_getKV];
        CAI_virtualGroupMirror set [_groupId, _map];
    };
} forEach _orders;

true

