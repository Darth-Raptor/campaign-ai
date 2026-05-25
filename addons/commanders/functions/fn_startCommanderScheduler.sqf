if (!isServer) exitWith { false };
if (!CAI_systemsEnabled) exitWith { false };
if (!isNil "CAI_commanderSchedulerRunning" && {CAI_commanderSchedulerRunning}) exitWith { true };

CAI_commanderSchedulerRunning = true;

[] spawn {
    ["[CAI CMD]", "Commander scheduler started."] call CAI_fnc_log;
    while {CAI_commanderSchedulerRunning} do {
        if (CAI_systemsEnabled && {CAI_initialized}) then {
            {
                private _commanderId = [_y, "commanderId", _x] call CAI_fnc_getKV;
                [_commanderId] call CAI_fnc_commanderCycle;
            } forEach CAI_commanderMirror;
        };
        sleep 120;
    };
};

true

