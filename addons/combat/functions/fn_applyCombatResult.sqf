params [
    ["_results", [], [[]]]
];

CAI_lastCombatResults = _results;
{
    private _outcome = [_x, "outcome", "UNKNOWN"] call CAI_fnc_getKV;
    private _attacker = [_x, "attackerGroupId", ""] call CAI_fnc_getKV;
    private _defender = [_x, "defenderGroupId", ""] call CAI_fnc_getKV;
    ["[CAI COMBAT]", format ["Combat result accepted: %1. Attacker: %2. Defender: %3.", _outcome, _attacker, _defender]] call CAI_fnc_log;
} forEach _results;

true

