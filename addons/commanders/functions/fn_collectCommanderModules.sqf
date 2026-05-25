private _commanders = [];
CAI_commanderMirror = createHashMap;

{
    private _index = _forEachIndex + 1;
    private _defaultId = format ["cmd_%1", _index toFixed 0];
    private _commanderId = _x getVariable ["CAI_commanderId", _defaultId];
    if (_commanderId isEqualTo "") then { _commanderId = _defaultId; };

    private _entry = [
        ["commanderId", _commanderId],
        ["name", _x getVariable ["CAI_commanderName", _commanderId]],
        ["side", _x getVariable ["CAI_side", "EAST"]],
        ["faction", _x getVariable ["CAI_faction", ""]],
        ["commanderType", _x getVariable ["CAI_commanderType", "conventional"]],
        ["posture", _x getVariable ["CAI_posture", "BALANCED"]],
        ["aoMarker", _x getVariable ["CAI_aoMarker", ""]],
        ["hqPosition", getPosATL _x],
        ["cycleTime", _x getVariable ["CAI_cycleTime", 120]],
        ["aggression", _x getVariable ["CAI_aggression", 50]],
        ["reservePercentage", _x getVariable ["CAI_reservePercentage", 20]],
        ["attackThreshold", _x getVariable ["CAI_attackThreshold", 1.25]],
        ["reinforcementThreshold", _x getVariable ["CAI_reinforcementThreshold", 60]],
        ["debugEnabled", _x getVariable ["CAI_debugEnabled", false]],
        ["persistenceEnabled", _x getVariable ["CAI_persistenceEnabled", true]]
    ];

    _commanders pushBack _entry;
    CAI_commanderMirror set [_commanderId, _entry];
} forEach CAI_moduleCommanders;

["[CAI CMD]", format ["Collected %1 commander module(s).", count _commanders]] call CAI_fnc_log;
_commanders

