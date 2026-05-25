params [
    ["_logic", objNull, [objNull]],
    ["_activated", true, [true]]
];

if (!_activated || {!isServer} || {isNull _logic}) exitWith {};

CAI_moduleDebug = _logic;
CAI_debugEnabled = _logic getVariable ["CAI_enableDebug", false];
CAI_debugMode = _logic getVariable ["CAI_debugMode", "BOTH"];
CAI_debugCommanderFilter = _logic getVariable ["CAI_commanderFilter", ""];
CAI_markerRefreshInterval = _logic getVariable ["CAI_markerRefreshInterval", 30];

["[CAI MODULE]", format ["Debug module registered. Enabled: %1. Mode: %2.", CAI_debugEnabled, CAI_debugMode]] call CAI_fnc_log;

