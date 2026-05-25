params [
    ["_results", [], [[]]]
];

CAI_lastCombatResults = _results;
{
    private _outcome = [_x, "outcome", "UNKNOWN"] call CAI_fnc_getKV;
    private _attacker = [_x, "attackerGroupId", ""] call CAI_fnc_getKV;
    private _defender = [_x, "defenderGroupId", ""] call CAI_fnc_getKV;
    private _groupUpdates = [_x, "groupUpdates", []] call CAI_fnc_getKV;
    private _objectiveUpdate = [_x, "objectiveUpdate", []] call CAI_fnc_getKV;

    {
        private _groupId = [_x, "groupId", ""] call CAI_fnc_getKV;
        private _group = CAI_virtualGroupMirror getOrDefault [_groupId, []];
        if (!(_group isEqualTo [])) then {
            private _map = [_group] call CAI_fnc_toHashMap;
            _map set ["strength", [_x, "strength", [_map, "strength", 0] call CAI_fnc_getKV] call CAI_fnc_getKV];
            _map set ["readiness", [_x, "readiness", [_map, "readiness", 100] call CAI_fnc_getKV] call CAI_fnc_getKV];
            _map set ["morale", [_x, "morale", [_map, "morale", 100] call CAI_fnc_getKV] call CAI_fnc_getKV];
            _map set ["status", [_x, "status", [_map, "status", "IDLE"] call CAI_fnc_getKV] call CAI_fnc_getKV];
            CAI_virtualGroupMirror set [_groupId, _map];
        };
    } forEach _groupUpdates;

    if (!(_objectiveUpdate isEqualTo [])) then {
        private _objectiveId = [_objectiveUpdate, "objectiveId", ""] call CAI_fnc_getKV;
        private _objective = CAI_objectiveMirror getOrDefault [_objectiveId, []];
        if (!(_objective isEqualTo [])) then {
            private _map = [_objective] call CAI_fnc_toHashMap;
            _map set ["owner", [_objectiveUpdate, "owner", [_map, "owner", "UNKNOWN"] call CAI_fnc_getKV] call CAI_fnc_getKV];
            _map set ["control", [_objectiveUpdate, "control", [_map, "control", 50] call CAI_fnc_getKV] call CAI_fnc_getKV];
            CAI_objectiveMirror set [_objectiveId, _map];
        };
    };

    ["[CAI COMBAT]", format ["Combat result accepted: %1. Attacker: %2. Defender: %3.", _outcome, _attacker, _defender]] call CAI_fnc_log;
} forEach _results;

if (CAI_debugEnabled && {(count _results) > 0}) then {
    [] call CAI_fnc_drawCombatDebug;
};

true
