if (!isServer) exitWith { false };

CAI_pythiaAvailable = false;
CAI_systemsEnabled = false;

if (isNil "py3_fnc_callExtension") exitWith {
    ["py3_fnc_callExtension missing or @Pythia not loaded"] call CAI_fnc_disableSystems;
    false
};

private _nativePing = ["pythia.ping", ["pong"]] call py3_fnc_callExtension;
if (!(_nativePing isEqualType []) || {(count _nativePing) isEqualTo 0}) exitWith {
    ["Pythia extension loaded, but built-in pythia.ping did not return data"] call CAI_fnc_disableSystems;
    false
};

["[CAI PYTHIA]", "Pythia extension ping successful."] call CAI_fnc_log;

private _response = ["CAIPython.api.ping", [], false] call CAI_fnc_pyCall;
if (!(_response isEqualType []) || {(count _response) < 4}) exitWith {
    ["CAIPython.api.ping returned an invalid envelope"] call CAI_fnc_disableSystems;
    false
};

private _success = _response select 0;
private _status = _response select 1;
private _payload = _response select 2;

if (!_success) exitWith {
    private _reason = if (_status isEqualTo "INVALID_PYTHON_ENVELOPE") then {
        "Pythia extension is available, but CAIPython.api.ping did not return the Campaign AI envelope. Verify @Campaign_AI\python_code\$PYTHIA$, __init__.py, and api.py are staged."
    } else {
        format ["CAIPython.api.ping failed with status %1", _status]
    };
    [_reason] call CAI_fnc_disableSystems;
    false
};

private _package = [_payload, "package", "CAIPython"] call CAI_fnc_getKV;
private _version = [_payload, "version", "unknown"] call CAI_fnc_getKV;

CAI_pythiaAvailable = true;
CAI_systemsEnabled = true;
CAI_failureReason = "";

["[CAI PYTHIA]", format ["Ping successful. Package: %1. Version: %2.", _package, _version]] call CAI_fnc_log;
true

