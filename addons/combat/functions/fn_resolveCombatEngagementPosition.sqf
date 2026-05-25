params [
    ["_engagement", [], [[]]]
];

private _position = [_engagement, "position", []] call CAI_fnc_getKV;
if ((_position isEqualType []) && {(count _position) >= 2}) exitWith { _position };

private _objectiveId = [_engagement, "objectiveId", ""] call CAI_fnc_getKV;
if (!(_objectiveId isEqualTo "")) then {
    private _objective = CAI_objectiveMirror getOrDefault [_objectiveId, []];
    if (!(_objective isEqualTo [])) then {
        _position = [_objective, "position", [0, 0, 0]] call CAI_fnc_getKV;
    };
};

if ((_position isEqualType []) && {(count _position) >= 2}) exitWith { _position };

private _attackerId = [_engagement, "attackerGroupId", ""] call CAI_fnc_getKV;
private _defenderId = [_engagement, "defenderGroupId", ""] call CAI_fnc_getKV;
private _attacker = CAI_virtualGroupMirror getOrDefault [_attackerId, []];
private _defender = CAI_virtualGroupMirror getOrDefault [_defenderId, []];

if (_attacker isEqualTo [] || {_defender isEqualTo []}) exitWith { [0, 0, 0] };

private _attackerPosition = [_attacker, "position", [0, 0, 0]] call CAI_fnc_getKV;
private _defenderPosition = [_defender, "position", [0, 0, 0]] call CAI_fnc_getKV;

[
    ((_attackerPosition param [0, 0, [0]]) + (_defenderPosition param [0, 0, [0]])) / 2,
    ((_attackerPosition param [1, 0, [0]]) + (_defenderPosition param [1, 0, [0]])) / 2,
    ((_attackerPosition param [2, 0, [0]]) + (_defenderPosition param [2, 0, [0]])) / 2
]
