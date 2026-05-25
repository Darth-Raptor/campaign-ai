{
    private _objective = [_x, "objectiveId", ""] call CAI_fnc_getKV;
    private _outcome = [_x, "outcome", "UNKNOWN"] call CAI_fnc_getKV;
    private _reason = [_x, "reason", ""] call CAI_fnc_getKV;
    ["[CAI COMBAT]", format ["Objective: %1 | Outcome: %2 | Reason: %3", _objective, _outcome, _reason]] call CAI_fnc_log;
} forEach CAI_lastCombatResults;

true

