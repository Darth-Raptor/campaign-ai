params [
    ["_commanderId", "", [""]]
];

private _commander = CAI_commanderMirror getOrDefault [_commanderId, []];
if (_commander isEqualTo []) exitWith { false };
private _map = [_commander] call CAI_fnc_toHashMap;
_map set ["paused", false];
CAI_commanderMirror set [_commanderId, _map];
["[CAI CMD]", format ["Commander resumed: %1.", _commanderId]] call CAI_fnc_log;
true

