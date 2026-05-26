params [
    ["_reason", "Unknown failure", [""]]
];

CAI_pythiaAvailable = false;
CAI_systemsEnabled = false;
CAI_failureReason = _reason;
CAI_initialized = false;
CAI_mapIndexingActive = false;
if (!(isNil "CAI_worldModelActive")) then { CAI_worldModelActive = false; };

["[CAI CORE]", "Campaign AI systems disabled. Mission will continue."] call CAI_fnc_log;
["[CAI CORE]", format ["Reason: %1", _reason]] call CAI_fnc_log;

true
