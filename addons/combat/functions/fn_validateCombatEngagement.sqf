params [
    ["_engagement", [], [[]]],
    ["_proximityRadius", CAI_combatPlayerProximityRadius, [0]]
];

private _attackerId = [_engagement, "attackerGroupId", ""] call CAI_fnc_getKV;
private _defenderId = [_engagement, "defenderGroupId", ""] call CAI_fnc_getKV;
private _objectiveId = [_engagement, "objectiveId", ""] call CAI_fnc_getKV;
private _position = [_engagement] call CAI_fnc_resolveCombatEngagementPosition;
private _reason = "";

private _validPosition = {
    params [["_pos", [], [[]]]];
    if ((count _pos) < 2) exitWith { false };
    private _xValue = _pos param [0, 0, [0]];
    private _yValue = _pos param [1, 0, [0]];
    (abs _xValue) <= 1000000 && {(abs _yValue) <= 1000000}
};

if (_attackerId isEqualTo "" || {_defenderId isEqualTo ""}) then { _reason = "missing group id"; };
if (_reason isEqualTo "" && {_attackerId isEqualTo _defenderId}) then { _reason = "attacker and defender are the same group"; };
if (_reason isEqualTo "" && {(CAI_virtualGroupMirror getOrDefault [_attackerId, []]) isEqualTo []}) then { _reason = "attacker group does not exist"; };
if (_reason isEqualTo "" && {(CAI_virtualGroupMirror getOrDefault [_defenderId, []]) isEqualTo []}) then { _reason = "defender group does not exist"; };
if (_reason isEqualTo "" && {!(_objectiveId isEqualTo "") && {(CAI_objectiveMirror getOrDefault [_objectiveId, []]) isEqualTo []}}) then { _reason = "objective does not exist"; };
if (_reason isEqualTo "" && {!([_position] call _validPosition)}) then { _reason = "engagement position outside safe bounds"; };

if (_reason isEqualTo "") then {
    private _attacker = CAI_virtualGroupMirror get _attackerId;
    private _defender = CAI_virtualGroupMirror get _defenderId;
    private _attackerSide = [_attacker, "side", "UNKNOWN"] call CAI_fnc_getKV;
    private _defenderSide = [_defender, "side", "UNKNOWN"] call CAI_fnc_getKV;
    if (_attackerSide isEqualTo _defenderSide) then { _reason = "groups are on the same side"; };
};

if (_reason isEqualTo "" && {({alive _x && {(_x distance2D _position) < _proximityRadius}} count allPlayers) > 0}) then {
    _reason = "players are nearby";
};

if (!(_reason isEqualTo "")) exitWith {
    ["[CAI COMBAT]", format ["Skipped combat engagement %1 vs %2. Reason: %3.", _attackerId, _defenderId, _reason]] call CAI_fnc_log;
    [false, [], _reason]
};

[
    true,
    [
        ["attackerGroupId", _attackerId],
        ["defenderGroupId", _defenderId],
        ["objectiveId", _objectiveId],
        ["position", _position],
        ["playersNearby", false]
    ],
    ""
]
