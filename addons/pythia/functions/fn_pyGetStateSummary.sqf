private _response = ["CAIPython.api.get_state_summary", [], false] call CAI_fnc_pyCall;
if ((_response select 0) isEqualTo true) then {
    CAI_lastPythonStateSummary = _response select 2;
};
_response

