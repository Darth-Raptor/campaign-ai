if (!isServer) exitWith {};

[] spawn {
    sleep 2;

    private _fixtureDeadline = time + 8;
    waitUntil {
        sleep 0.1;
        !(missionNamespace getVariable ["CAI_TEST_fixtureRegistrationPending", false]) || {time > _fixtureDeadline}
    };

    if (!CAI_systemsEnabled) exitWith {
        ["[CAI MODULE]", "Module initialization skipped because Campaign AI is disabled."] call CAI_fnc_log;
    };

    private _objectives = [] call CAI_fnc_collectObjectiveModules;
    private _commanders = [] call CAI_fnc_collectCommanderModules;
    private _groups = [] call CAI_fnc_collectVirtualForceModules;

    if ((count _objectives) isEqualTo 0 && {(count _commanders) isEqualTo 0} && {(count _groups) isEqualTo 0}) then {
        ["[CAI MODULE]", "No Eden modules found. Using sample state for Pythia proof path."] call CAI_fnc_log;
        _objectives = [[
            ["objectiveId", "obj_sample_01"],
            ["name", "Sample Objective"],
            ["objectiveType", "outpost"],
            ["initialOwner", "EAST"],
            ["owner", "EAST"],
            ["priority", 50],
            ["radius", 300],
            ["size", "medium"],
            ["terrainType", "mixed"],
            ["garrisonSlots", 0],
            ["position", [0, 0, 0]],
            ["debugEnabled", true]
        ]];
        _commanders = [[
            ["commanderId", "red_cmd_01"],
            ["name", "Sample REDFOR Commander"],
            ["side", "EAST"],
            ["faction", ""],
            ["commanderType", "conventional"],
            ["posture", "BALANCED"],
            ["aoMarker", ""],
            ["hqPosition", [0, 0, 0]],
            ["cycleTime", 120],
            ["aggression", 50],
            ["reservePercentage", 20],
            ["attackThreshold", 1.25],
            ["reinforcementThreshold", 60],
            ["debugEnabled", true],
            ["persistenceEnabled", true]
        ]];
        _groups = [[
            ["groupId", "grp_red_001"],
            ["name", "Sample REDFOR Platoon"],
            ["side", "EAST"],
            ["faction", ""],
            ["commanderId", "red_cmd_01"],
            ["forceSize", "platoon"],
            ["unitType", "infantry"],
            ["mobility", "foot"],
            ["position", [0, 0, 0]],
            ["initialObjective", "obj_sample_01"],
            ["debugEnabled", true],
            ["manualOverride", false]
        ]];

        CAI_objectiveMirror set ["obj_sample_01", _objectives select 0];
        CAI_commanderMirror set ["red_cmd_01", _commanders select 0];
        CAI_virtualGroupMirror set ["grp_red_001", _groups select 0];
        CAI_debugEnabled = true;
    };

    private _campaignId = format ["%1_%2", worldName, missionName];
    private _payload = [
        ["campaignId", _campaignId],
        ["worldName", worldName],
        ["missionName", missionName],
        ["objectives", _objectives],
        ["commanders", _commanders],
        ["virtualGroups", _groups],
        ["settings", [
            ["debugEnabled", CAI_debugEnabled],
            ["debugMode", CAI_debugMode],
            ["debugCommanderFilter", CAI_debugCommanderFilter],
            ["markerRefreshInterval", CAI_markerRefreshInterval],
            ["backendEnabled", false],
            ["clientPythonEnabled", false],
            ["liveSpawnLifecycleEnabled", false]
        ]]
    ];

    private _initResponse = [_payload] call CAI_fnc_pyInitState;
    if (!((_initResponse select 0) isEqualTo true)) exitWith {};

    private _savePayload = [["campaignId", _campaignId], ["saveName", "autosave"]];
    private _saveResponse = [_savePayload] call CAI_fnc_pySaveSnapshot;
    if (!((_saveResponse select 0) isEqualTo true)) exitWith {};

    private _loadResponse = [_savePayload] call CAI_fnc_pyLoadSnapshot;
    if ((_loadResponse select 0) isEqualTo true) then {
        ["[CAI MODULE]", "Initial Pythia save/load proof path completed."] call CAI_fnc_log;
    };

    if (CAI_debugEnabled) then {
        private _debugPayload = [
            ["debugMode", CAI_debugMode],
            ["commanderId", CAI_debugCommanderFilter],
            ["gameTime", [] call CAI_fnc_getTime]
        ];
        private _debugResponse = [_debugPayload] call CAI_fnc_pyGetDebugSnapshot;
        if ((_debugResponse select 0) isEqualTo true) then {
            [_debugResponse select 2] call CAI_fnc_drawCommanderDebug;
        };
    };

    [] call CAI_fnc_startCommanderScheduler;
};
