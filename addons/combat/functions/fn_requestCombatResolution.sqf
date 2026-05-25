params [
    ["_engagements", [], [[]]],
    ["_autoDetect", false, [true]]
];

if (!isServer || {!CAI_systemsEnabled}) exitWith {
    [false, "CAI_COMBAT_DISABLED", [], ["[CAI COMBAT] Combat resolution skipped"]]
};

private _safeEngagements = [];
if (_autoDetect) then {
    ["[CAI COMBAT]", "Auto-detect requested. V1.0 only resolves engagements after SQF player-proximity filtering. Provide explicit engagement payloads."] call CAI_fnc_log;
};

{
    private _position = [_x, "position", [0, 0, 0]] call CAI_fnc_getKV;
    private _playersNearby = ({(_x distance2D _position) < 1000} count allPlayers) > 0;
    if (_playersNearby) then {
        ["[CAI COMBAT]", "Skipped virtual combat because players are nearby."] call CAI_fnc_log;
    } else {
        _safeEngagements pushBack (_x + [["playersNearby", false]]);
    };
} forEach _engagements;

private _payload = [
    ["gameTime", [] call CAI_fnc_getTime],
    ["engagements", _safeEngagements],
    ["autoDetect", false],
    ["randomness", "NORMAL"]
];

private _response = ["CAIPython.api.resolve_combat_batch", [_payload], false] call CAI_fnc_pyCall;
if ((_response select 0) isEqualTo true) then {
    private _payloadOut = _response select 2;
    private _results = [_payloadOut, "results", []] call CAI_fnc_getKV;
    private _accepted = [];
    {
        if ([_x] call CAI_fnc_validateCombatResult) then {
            _accepted pushBack _x;
        };
    } forEach _results;
    [_accepted] call CAI_fnc_applyCombatResult;
};

_response
