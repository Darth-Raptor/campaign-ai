{
    private _objective = [_x, "objectiveId", ""] call CAI_fnc_getKV;
    private _outcome = [_x, "outcome", "UNKNOWN"] call CAI_fnc_getKV;
    private _attacker = [_x, "attackerGroupId", ""] call CAI_fnc_getKV;
    private _defender = [_x, "defenderGroupId", ""] call CAI_fnc_getKV;
    private _report = [_x, "combatReport", ""] call CAI_fnc_getKV;
    private _reason = [_x, "reason", ""] call CAI_fnc_getKV;
    ["[CAI COMBAT]", format ["Report: %1 vs %2 | Objective: %3 | Outcome: %4 | %5 | Reason: %6", _attacker, _defender, _objective, _outcome, _report, _reason]] call CAI_fnc_log;
} forEach CAI_lastCombatResults;

true
