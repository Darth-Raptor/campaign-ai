params [
    ["_payload", [], [[]]]
];

private _response = ["CAIPython.api.load_snapshot", [_payload], true] call CAI_fnc_pyCall;
if ((_response select 0) isEqualTo true) then {
    CAI_lastPythonStateSummary = [_response select 2, "summary", []] call CAI_fnc_getKV;
};
_response

