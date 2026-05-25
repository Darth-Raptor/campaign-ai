params [
    ["_radius", CAI_combatAutoDetectRadius, [0]]
];

private _ids = keys CAI_virtualGroupMirror;
private _engagements = [];

if ((count _ids) < 2) exitWith { _engagements };

for "_i" from 0 to ((count _ids) - 2) do {
    private _attackerId = _ids select _i;
    private _attacker = CAI_virtualGroupMirror get _attackerId;
    private _attackerSide = [_attacker, "side", "UNKNOWN"] call CAI_fnc_getKV;
    private _attackerStrength = [_attacker, "strength", 1] call CAI_fnc_getKV;
    private _attackerPosition = [_attacker, "position", [0, 0, 0]] call CAI_fnc_getKV;

    for "_j" from (_i + 1) to ((count _ids) - 1) do {
        private _defenderId = _ids select _j;
        private _defender = CAI_virtualGroupMirror get _defenderId;
        private _defenderSide = [_defender, "side", "UNKNOWN"] call CAI_fnc_getKV;
        private _defenderStrength = [_defender, "strength", 1] call CAI_fnc_getKV;
        private _defenderPosition = [_defender, "position", [0, 0, 0]] call CAI_fnc_getKV;

        if (
            _attackerStrength > 0 &&
            {_defenderStrength > 0} &&
            {!(_attackerSide isEqualTo _defenderSide)} &&
            {(_attackerPosition distance2D _defenderPosition) <= _radius}
        ) then {
            private _objectiveId = [_attacker, "currentObjectiveId", [_attacker, "initialObjective", ""] call CAI_fnc_getKV] call CAI_fnc_getKV;
            if (_objectiveId isEqualTo "") then {
                _objectiveId = [_defender, "currentObjectiveId", [_defender, "initialObjective", ""] call CAI_fnc_getKV] call CAI_fnc_getKV;
            };

            _engagements pushBack [
                ["attackerGroupId", _attackerId],
                ["defenderGroupId", _defenderId],
                ["objectiveId", _objectiveId],
                ["position", [
                    ((_attackerPosition param [0, 0, [0]]) + (_defenderPosition param [0, 0, [0]])) / 2,
                    ((_attackerPosition param [1, 0, [0]]) + (_defenderPosition param [1, 0, [0]])) / 2,
                    ((_attackerPosition param [2, 0, [0]]) + (_defenderPosition param [2, 0, [0]])) / 2
                ]]
            ];
        };
    };
};

["[CAI COMBAT]", format ["Auto-detected %1 candidate combat engagement(s).", count _engagements]] call CAI_fnc_log;
_engagements
