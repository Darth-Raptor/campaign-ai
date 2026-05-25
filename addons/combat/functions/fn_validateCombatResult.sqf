params [
    ["_result", [], [[]]],
    ["_proximityRadius", CAI_combatPlayerProximityRadius, [0]]
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
private _objectiveId = [_result, "objectiveId", ""] call CAI_fnc_getKV;
private _outcome = [_result, "outcome", ""] call CAI_fnc_getKV;
private _attackerLoss = [_result, "attackerLossPercent", -1] call CAI_fnc_getKV;
private _defenderLoss = [_result, "defenderLossPercent", -1] call CAI_fnc_getKV;
private _attackerReadinessDelta = [_result, "attackerReadinessDelta", 0] call CAI_fnc_getKV;
private _defenderReadinessDelta = [_result, "defenderReadinessDelta", 0] call CAI_fnc_getKV;
private _attackerMoraleDelta = [_result, "attackerMoraleDelta", 0] call CAI_fnc_getKV;
private _defenderMoraleDelta = [_result, "defenderMoraleDelta", 0] call CAI_fnc_getKV;
private _objectiveControlDelta = [_result, "objectiveControlDelta", 0] call CAI_fnc_getKV;
private _position = [_result] call CAI_fnc_resolveCombatEngagementPosition;
private _groupUpdates = [_result, "groupUpdates", []] call CAI_fnc_getKV;
private _objectiveUpdate = [_result, "objectiveUpdate", []] call CAI_fnc_getKV;

private _asNumber = {
    params ["_value", "_default"];
    if (_value isEqualType 0) exitWith { _value };
    if (_value isEqualType "") exitWith { parseNumber _value };
    _default
};

private _validPosition = {
    params [["_pos", [], [[]]]];
    if ((count _pos) < 2) exitWith { false };
    private _xValue = _pos param [0, 0, [0]];
    private _yValue = _pos param [1, 0, [0]];
    (abs _xValue) <= 1000000 && {(abs _yValue) <= 1000000}
};

_attackerLoss = [_attackerLoss, -1] call _asNumber;
_defenderLoss = [_defenderLoss, -1] call _asNumber;
_attackerReadinessDelta = [_attackerReadinessDelta, 0] call _asNumber;
_defenderReadinessDelta = [_defenderReadinessDelta, 0] call _asNumber;
_attackerMoraleDelta = [_attackerMoraleDelta, 0] call _asNumber;
_defenderMoraleDelta = [_defenderMoraleDelta, 0] call _asNumber;
_objectiveControlDelta = [_objectiveControlDelta, 0] call _asNumber;

if (_attacker isEqualTo "" || {_defender isEqualTo ""}) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: missing group id."] call CAI_fnc_log;
    false
};

if ((CAI_virtualGroupMirror getOrDefault [_attacker, []]) isEqualTo [] || {(CAI_virtualGroupMirror getOrDefault [_defender, []]) isEqualTo []}) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: group does not exist in SQF mirror."] call CAI_fnc_log;
    false
};

if (!(_objectiveId isEqualTo "") && {(CAI_objectiveMirror getOrDefault [_objectiveId, []]) isEqualTo []}) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: objective does not exist in SQF mirror."] call CAI_fnc_log;
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

if (
    (abs _attackerReadinessDelta) > 100 ||
    {(abs _defenderReadinessDelta) > 100} ||
    {(abs _attackerMoraleDelta) > 100} ||
    {(abs _defenderMoraleDelta) > 100} ||
    {(abs _objectiveControlDelta) > 100}
) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: delta outside safe bounds."] call CAI_fnc_log;
    false
};

if (!([_position] call _validPosition)) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: result position outside safe bounds."] call CAI_fnc_log;
    false
};

if (({alive _x && {(_x distance2D _position) < _proximityRadius}} count allPlayers) > 0) exitWith {
    ["[CAI COMBAT]", "Rejected combat result. Reason: players are near the engagement."] call CAI_fnc_log;
    false
};

private _reason = "";
if !(_groupUpdates isEqualType []) then { _reason = "groupUpdates is not an array"; };
if (_reason isEqualTo "") then {
    {
        if (_reason isEqualTo "") then {
            private _groupId = [_x, "groupId", ""] call CAI_fnc_getKV;
            private _strength = [[_x, "strength", -1] call CAI_fnc_getKV, -1] call _asNumber;
            private _readiness = [[_x, "readiness", -1] call CAI_fnc_getKV, -1] call _asNumber;
            private _morale = [[_x, "morale", -1] call CAI_fnc_getKV, -1] call _asNumber;
            if (_groupId isEqualTo "") then { _reason = "group update missing group id"; };
            if (_reason isEqualTo "" && {(CAI_virtualGroupMirror getOrDefault [_groupId, []]) isEqualTo []}) then { _reason = "group update references unknown group"; };
            if (_reason isEqualTo "" && {_strength < 0 || {_strength > 5000}}) then { _reason = "group strength outside safe bounds"; };
            if (_reason isEqualTo "" && {_readiness < 0 || {_readiness > 100} || {_morale < 0} || {_morale > 100}}) then { _reason = "group readiness/morale outside safe bounds"; };
        };
    } forEach _groupUpdates;
};

if (!(_reason isEqualTo "")) exitWith {
    ["[CAI COMBAT]", format ["Rejected combat result. Reason: %1.", _reason]] call CAI_fnc_log;
    false
};

if (!(_objectiveUpdate isEqualTo [])) then {
    private _updateObjectiveId = [_objectiveUpdate, "objectiveId", ""] call CAI_fnc_getKV;
    private _control = [[_objectiveUpdate, "control", -1] call CAI_fnc_getKV, -1] call _asNumber;
    private _owner = [_objectiveUpdate, "owner", "UNKNOWN"] call CAI_fnc_getKV;
    if (_updateObjectiveId isEqualTo "" || {(CAI_objectiveMirror getOrDefault [_updateObjectiveId, []]) isEqualTo []}) then {
        _reason = "objective update references unknown objective";
    };
    if (_reason isEqualTo "" && {_control < 0 || {_control > 100}}) then {
        _reason = "objective control outside safe bounds";
    };
    if (_reason isEqualTo "" && {!(_owner in ["WEST", "EAST", "GUER", "CIV", "UNKNOWN"])}) then {
        _reason = format ["invalid objective owner %1", _owner];
    };
};

if (!(_reason isEqualTo "")) exitWith {
    ["[CAI COMBAT]", format ["Rejected combat result. Reason: %1.", _reason]] call CAI_fnc_log;
    false
};

true
