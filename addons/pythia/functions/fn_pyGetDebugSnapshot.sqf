params [
    ["_payload", [], [[]]]
];

private _response = ["CAIPython.api.get_debug_snapshot", [_payload], false] call CAI_fnc_pyCall;
if ((_response select 0) isEqualTo true) then {
    CAI_lastDebugSnapshot = _response select 2;
};
_response

