params [
    ["_functionName", "", [""]],
    ["_args", [], [[]]],
    ["_disableOnFailure", true, [true]]
];

if (!isServer) exitWith {
    [false, "SQF_NOT_SERVER", [], ["[CAI PYTHIA] Rejected Python call outside server authority"]]
};

private _isBootstrapCall = _functionName isEqualTo "CAIPython.api.ping";

if (!_isBootstrapCall && {!CAI_systemsEnabled}) exitWith {
    [false, "CAI_SYSTEMS_DISABLED", [], [format ["[CAI PYTHIA] Skipped %1 because Campaign AI is disabled", _functionName]]]
};

if (isNil "py3_fnc_callExtension") exitWith {
    private _reason = "py3_fnc_callExtension missing or @Pythia not loaded";
    if (_disableOnFailure) then { [_reason] call CAI_fnc_disableSystems; };
    [false, "PYTHIA_MISSING", [], [format ["[CAI PYTHIA] %1", _reason]]]
};

CAI_lastPythonCall = _functionName;

private _response = [_functionName, _args] call py3_fnc_callExtension;
CAI_lastPythonRawResponse = _response;

private _validEnvelope = (_response isEqualType [])
    && {(count _response) isEqualTo 4}
    && {(_response select 0) isEqualType true}
    && {(_response select 1) isEqualType ""}
    && {(_response select 3) isEqualType []};

if (!_validEnvelope) exitWith {
    CAI_lastPythonStatus = "INVALID_ENVELOPE";
    CAI_lastPythonError = if ((_response isEqualType []) && {(count _response) isEqualTo 0}) then {
        format [
            "Pythia returned an empty response for %1. This usually means the Python module/function was not recognized. Verify @Campaign_AI\python_code\$PYTHIA$, __init__.py, and api.py are staged.",
            _functionName
        ]
    } else {
        format ["Invalid Python response envelope from %1", _functionName]
    };
    if (_disableOnFailure) then { [CAI_lastPythonError] call CAI_fnc_disableSystems; };
    [false, "INVALID_PYTHON_ENVELOPE", [], [format ["[CAI PYTHIA] %1", CAI_lastPythonError]]]
};

private _success = _response select 0;
private _status = _response select 1;
private _logs = _response select 3;

CAI_lastPythonStatus = _status;
if (!_success) then {
    CAI_lastPythonError = format ["%1 failed with status %2", _functionName, _status];
};

if (CAI_debugEnabled) then {
    {
        ["[CAI PYTHIA]", _x] call CAI_fnc_log;
    } forEach _logs;
};

if (!_success && {_disableOnFailure}) then {
    [format ["Python call failed: %1 (%2)", _functionName, _status]] call CAI_fnc_disableSystems;
};

_response
