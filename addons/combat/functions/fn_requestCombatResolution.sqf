params [
    ["_engagements", [], [[]]],
    ["_autoDetect", false, [true]],
    ["_randomness", "NORMAL", [""]]
];

if (!isServer || {!CAI_systemsEnabled}) exitWith {
    [false, "CAI_COMBAT_DISABLED", [], ["[CAI COMBAT] Combat resolution skipped"]]
};

private _safeEngagements = [];
if (_autoDetect) then {
    _engagements append ([] call CAI_fnc_detectCombatEngagements);
};

{
    private _validated = [_x, CAI_combatPlayerProximityRadius] call CAI_fnc_validateCombatEngagement;
    if ((_validated select 0) isEqualTo true) then {
        _safeEngagements pushBack (_validated select 1);
    };
} forEach _engagements;

private _payload = [
    ["gameTime", [] call CAI_fnc_getTime],
    ["engagements", _safeEngagements],
    ["autoDetect", false],
    ["randomness", _randomness]
];

private _response = ["CAIPython.api.resolve_combat_batch", [_payload], false] call CAI_fnc_pyCall;
if ((_response select 0) isEqualTo true) then {
    private _payloadOut = _response select 2;
    private _results = [_payloadOut, "results", []] call CAI_fnc_getKV;
    private _accepted = [];
    {
        if ([_x, CAI_combatPlayerProximityRadius] call CAI_fnc_validateCombatResult) then {
            _accepted pushBack _x;
        };
    } forEach _results;
    [_accepted] call CAI_fnc_applyCombatResult;
};

_response
