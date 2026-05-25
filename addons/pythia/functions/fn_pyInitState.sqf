params [
    ["_payload", [], [[]]]
];

private _response = ["CAIPython.api.init_state", [_payload], true] call CAI_fnc_pyCall;
if ((_response select 0) isEqualTo true) then {
    CAI_initialized = true;
    CAI_lastPythonStateSummary = (_response select 2);
    ["[CAI PYTHIA]", "Python campaign state initialized."] call CAI_fnc_log;
};
_response

