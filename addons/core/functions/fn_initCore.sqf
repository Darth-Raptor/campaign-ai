/*
    Initializes shared Campaign AI globals. Simulation work remains disabled
    until the Pythia addon successfully verifies CAIPython.
*/

if (!isServer) exitWith {};

if (isNil "CAI_initialized") then { CAI_initialized = false; };
if (isNil "CAI_pythiaAvailable") then { CAI_pythiaAvailable = false; };
if (isNil "CAI_systemsEnabled") then { CAI_systemsEnabled = false; };
if (isNil "CAI_failureReason") then { CAI_failureReason = ""; };
if (isNil "CAI_debugEnabled") then { CAI_debugEnabled = false; };
if (isNil "CAI_debugMode") then { CAI_debugMode = "BOTH"; };
if (isNil "CAI_debugCommanderFilter") then { CAI_debugCommanderFilter = ""; };
if (isNil "CAI_markerRefreshInterval") then { CAI_markerRefreshInterval = 30; };

CAI_moduleObjectives = [];
CAI_moduleCommanders = [];
CAI_moduleVirtualForces = [];
CAI_moduleDebug = objNull;

CAI_lastPythonStateSummary = [];
CAI_lastDebugSnapshot = [];
CAI_lastCommanderCycle = 0;
CAI_lastPythonCall = "";
CAI_lastPythonStatus = "";
CAI_lastPythonError = "";

CAI_objectiveMirror = createHashMap;
CAI_virtualGroupMirror = createHashMap;
CAI_commanderMirror = createHashMap;
CAI_debugMarkers = [];
CAI_observedEvents = [];
CAI_lastCombatResults = [];

["[CAI CORE]", "Campaign AI core initialized."] call CAI_fnc_log;

