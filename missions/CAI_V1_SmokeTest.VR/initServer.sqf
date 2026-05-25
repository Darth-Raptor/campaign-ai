if (!isServer) exitWith {};

missionNamespace setVariable ["CAI_TEST_fixtureRegistrationPending", true, true];

[] spawn {
    waitUntil {
        sleep 0.1;
        !isNil "CAI_fnc_registerObjective"
            && {!isNil "CAI_fnc_registerCommander"}
            && {!isNil "CAI_fnc_registerVirtualGroup"}
            && {!isNil "CAI_fnc_moduleDebug"}
    };

    private _logicGroup = createGroup sideLogic;
    private _createLogic = {
        params ["_className", "_position"];
        private _logic = _logicGroup createUnit ["Logic", _position, [], 0, "NONE"];
        if (isNull _logic) then {
            _logic = "Logic" createVehicle _position;
        };
        _logic setPosATL _position;
        _logic
    };

    private _combatCenter = [5200, 5000, 0];

    private _redObjective = ["CAI_ModuleObjective", [5000, 5000, 0]] call _createLogic;
    _redObjective setVariable ["CAI_objectiveId", "obj_red_hq", true];
    _redObjective setVariable ["CAI_objectiveName", "REDFOR HQ", true];
    _redObjective setVariable ["CAI_objectiveType", "hq", true];
    _redObjective setVariable ["CAI_initialOwner", "EAST", true];
    _redObjective setVariable ["CAI_control", 100, true];
    _redObjective setVariable ["CAI_priority", 80, true];
    _redObjective setVariable ["CAI_radius", 300, true];
    _redObjective setVariable ["CAI_size", "medium", true];
    _redObjective setVariable ["CAI_terrainType", "urban", true];
    _redObjective setVariable ["CAI_garrisonSlots", 4, true];
    _redObjective setVariable ["CAI_debugEnabled", true, true];
    [_redObjective] call CAI_fnc_registerObjective;

    private _blueObjective = ["CAI_ModuleObjective", [5400, 5000, 0]] call _createLogic;
    _blueObjective setVariable ["CAI_objectiveId", "obj_blue_outpost", true];
    _blueObjective setVariable ["CAI_objectiveName", "BLUEFOR Outpost", true];
    _blueObjective setVariable ["CAI_objectiveType", "outpost", true];
    _blueObjective setVariable ["CAI_initialOwner", "WEST", true];
    _blueObjective setVariable ["CAI_control", 50, true];
    _blueObjective setVariable ["CAI_priority", 70, true];
    _blueObjective setVariable ["CAI_radius", 300, true];
    _blueObjective setVariable ["CAI_size", "medium", true];
    _blueObjective setVariable ["CAI_terrainType", "mixed", true];
    _blueObjective setVariable ["CAI_garrisonSlots", 4, true];
    _blueObjective setVariable ["CAI_debugEnabled", true, true];
    [_blueObjective] call CAI_fnc_registerObjective;

    private _commander = ["CAI_ModuleCommander", [5000, 4800, 0]] call _createLogic;
    _commander setVariable ["CAI_commanderId", "red_cmd_01", true];
    _commander setVariable ["CAI_commanderName", "REDFOR Test Commander", true];
    _commander setVariable ["CAI_side", "EAST", true];
    _commander setVariable ["CAI_faction", "OPF_F", true];
    _commander setVariable ["CAI_commanderType", "conventional", true];
    _commander setVariable ["CAI_posture", "BALANCED", true];
    _commander setVariable ["CAI_aoMarker", "", true];
    _commander setVariable ["CAI_cycleTime", 120, true];
    _commander setVariable ["CAI_aggression", 50, true];
    _commander setVariable ["CAI_reservePercentage", 20, true];
    _commander setVariable ["CAI_attackThreshold", 1.25, true];
    _commander setVariable ["CAI_reinforcementThreshold", 60, true];
    _commander setVariable ["CAI_debugEnabled", true, true];
    _commander setVariable ["CAI_persistenceEnabled", true, true];
    [_commander] call CAI_fnc_registerCommander;

    private _redGroup = ["CAI_ModuleVirtualForces", [5075, 5000, 0]] call _createLogic;
    _redGroup setVariable ["CAI_groupId", "grp_red_001", true];
    _redGroup setVariable ["CAI_groupName", "REDFOR Test Company", true];
    _redGroup setVariable ["CAI_side", "EAST", true];
    _redGroup setVariable ["CAI_faction", "OPF_F", true];
    _redGroup setVariable ["CAI_commanderId", "red_cmd_01", true];
    _redGroup setVariable ["CAI_forceSize", "company", true];
    _redGroup setVariable ["CAI_unitType", "infantry", true];
    _redGroup setVariable ["CAI_mobility", "foot", true];
    _redGroup setVariable ["CAI_initialObjective", "obj_red_hq", true];
    _redGroup setVariable ["CAI_debugEnabled", true, true];
    [_redGroup] call CAI_fnc_registerVirtualGroup;

    private _blueGroup = ["CAI_ModuleVirtualForces", [5325, 5000, 0]] call _createLogic;
    _blueGroup setVariable ["CAI_groupId", "grp_blue_001", true];
    _blueGroup setVariable ["CAI_groupName", "BLUEFOR Test Platoon", true];
    _blueGroup setVariable ["CAI_side", "WEST", true];
    _blueGroup setVariable ["CAI_faction", "BLU_F", true];
    _blueGroup setVariable ["CAI_commanderId", "", true];
    _blueGroup setVariable ["CAI_forceSize", "platoon", true];
    _blueGroup setVariable ["CAI_unitType", "infantry", true];
    _blueGroup setVariable ["CAI_mobility", "foot", true];
    _blueGroup setVariable ["CAI_initialObjective", "obj_blue_outpost", true];
    _blueGroup setVariable ["CAI_debugEnabled", true, true];
    [_blueGroup] call CAI_fnc_registerVirtualGroup;

    private _debug = ["CAI_ModuleDebug", [5000, 4700, 0]] call _createLogic;
    _debug setVariable ["CAI_enableDebug", true, true];
    _debug setVariable ["CAI_debugMode", "BOTH", true];
    _debug setVariable ["CAI_commanderFilter", "", true];
    _debug setVariable ["CAI_markerRefreshInterval", 30, true];
    [_debug, true] call CAI_fnc_moduleDebug;

    missionNamespace setVariable ["CAI_TEST_phase7CombatEngagement", [[
        ["attackerGroupId", "grp_red_001"],
        ["defenderGroupId", "grp_blue_001"],
        ["objectiveId", "obj_blue_outpost"],
        ["position", _combatCenter]
    ]], true];

    missionNamespace setVariable ["CAI_TEST_fixtureRegistrationPending", false, true];
    ["[CAI TEST]", "CAI_V1_SmokeTest fixture registered module-compatible logic objects."] call CAI_fnc_log;
};

[] spawn {
    waitUntil {
        sleep 0.5;
        (missionNamespace getVariable ["CAI_systemsEnabled", false])
            && {missionNamespace getVariable ["CAI_initialized", false]}
    };

    sleep 8;

    private _engagements = missionNamespace getVariable ["CAI_TEST_phase7CombatEngagement", []];
    if ((count _engagements) isEqualTo 0) exitWith {};

    ["[CAI TEST]", "Triggering Phase 7 offscreen combat smoke check. Player start is outside the virtual-combat proximity radius."] call CAI_fnc_log;
    private _response = [_engagements, false, "NONE"] call CAI_fnc_requestCombatResolution;

    if ((_response select 0) isEqualTo true) then {
        private _payload = _response select 2;
        private _results = [_payload, "results", []] call CAI_fnc_getKV;
        private _skipped = [_payload, "skipped", []] call CAI_fnc_getKV;
        ["[CAI TEST]", format ["Phase 7 combat smoke response. Results: %1. Skipped: %2.", count _results, count _skipped]] call CAI_fnc_log;
    } else {
        ["[CAI TEST]", format ["Phase 7 combat smoke failed. Status: %1.", _response select 1]] call CAI_fnc_log;
    };
};
