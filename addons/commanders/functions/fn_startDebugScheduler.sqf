if (!isServer || {!CAI_systemsEnabled}) exitWith { false };
if (CAI_debugSchedulerStarted) exitWith { true };

CAI_debugSchedulerStarted = true;

[] spawn {
    while {isServer && {CAI_systemsEnabled}} do {
        private _interval = CAI_markerRefreshInterval max 5;
        sleep _interval;

        if (CAI_systemsEnabled && {CAI_debugEnabled}) then {
            private _debugPayload = [
                ["debugMode", CAI_debugMode],
                ["commanderId", CAI_debugCommanderFilter],
                ["gameTime", [] call CAI_fnc_getTime]
            ];
            private _debugResponse = [_debugPayload] call CAI_fnc_pyGetDebugSnapshot;
            if ((_debugResponse select 0) isEqualTo true) then {
                [_debugResponse select 2] call CAI_fnc_drawCommanderDebug;
                ["[CAI DEBUG]", format ["Debug markers refreshed. Interval: %1s.", _interval]] call CAI_fnc_log;
            };
        };
    };

    CAI_debugSchedulerStarted = false;
};

["[CAI DEBUG]", format ["Debug marker scheduler started. Interval: %1s.", CAI_markerRefreshInterval max 5]] call CAI_fnc_log;
true

