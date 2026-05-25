params [
    ["_result", [], [[]]]
];

private _allowedOutcomes = [
    "ATTACKER_DECISIVE_VICTORY",
    "ATTACKER_VICTORY",
    "ATTACKER_COSTLY_VICTORY",
    "ATTACKER_GAINED_GROUND",
    "STALEMATE",
    "DEFENDER_HOLD",
    "DEFENDER_SUCCESSFUL_DEFENSE",
    "ATTACKER_REPULSED",
    "ATTACKER_ROUTED",
    "DEFENDER_WITHDRAWAL",
    "BOTH_SIDES_BREAK_CONTACT"
];

private _attacker = [_result, "attackerGroupId", ""] call CAI_fnc_getKV;
private _defender = [_result, "defenderGroupId", ""] call CAI_fnc_getKV;
private _outcome = [_result, "outcome", ""] call CAI_fnc_getKV;
private _attackerLoss = [_result, "attackerLossPercent", -1] call CAI_fnc_getKV;
private _defenderLoss = [_result, "defenderLossPercent", -1] call CAI_fnc_getKV;

if (_attacker isEqualTo "" || {_defender isEqualTo ""}) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: missing group id."] call CAI_fnc_log;
    false
};

if !(_outcome in _allowedOutcomes) exitWith {
    ["[CAI COMBAT]", format ["Rejected combat result. Reason: invalid outcome %1.", _outcome]] call CAI_fnc_log;
    false
};

if (_attackerLoss < 0 || {_attackerLoss > 100} || {_defenderLoss < 0} || {_defenderLoss > 100}) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: loss percent outside safe bounds."] call CAI_fnc_log;
    false
};

true

