params [
    ["_commanderId", "", [""]]
];

if (!isServer || {!CAI_systemsEnabled} || {!CAI_initialized}) exitWith {
    [false, "CAI_CMD_DISABLED", [], ["[CAI CMD] Commander cycle skipped"]]
};

if (_commanderId isEqualTo "") exitWith {
    [false, "CAI_CMD_NO_COMMANDER", [], ["[CAI CMD] Commander cycle skipped. Missing commander id."]]
};

private _observedEvents = [] call CAI_fnc_collectObservedEvents;
private _payload = [
    ["commanderId", _commanderId],
    ["gameTime", [] call CAI_fnc_getTime],
    ["observedEvents", _observedEvents]
];

["[CAI CMD]", format ["Commander cycle started for %1.", _commanderId]] call CAI_fnc_log;
private _response = ["CAIPython.api.commander_cycle", [_payload], false] call CAI_fnc_pyCall;

if ((_response select 0) isEqualTo true) then {
    private _payloadOut = _response select 2;
    private _orders = [_payloadOut, "orders", []] call CAI_fnc_getKV;
    private _validated = [_orders, [] call CAI_fnc_getTime] call CAI_fnc_validateRecommendedOrders;
    private _accepted = _validated select 0;
    [_accepted] call CAI_fnc_applyRecommendedOrders;
    CAI_lastCommanderCycle = [] call CAI_fnc_getTime;

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
};

_response

