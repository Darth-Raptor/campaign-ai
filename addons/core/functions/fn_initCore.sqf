/*
    Initializes shared Campaign AI globals. Higher-level systems remain gated
    by Pythia availability and CAI_systemsEnabled.
*/

if (!isServer) exitWith {};

if (isNil "CAI_initialized") then { CAI_initialized = false; };
if (isNil "CAI_pythiaAvailable") then { CAI_pythiaAvailable = false; };
if (isNil "CAI_systemsEnabled") then { CAI_systemsEnabled = false; };
if (isNil "CAI_failureReason") then { CAI_failureReason = ""; };
if (isNil "CAI_debugEnabled") then { CAI_debugEnabled = false; };

CAI_lastPythonCall = "";
CAI_lastPythonStatus = "";
CAI_lastPythonError = "";
CAI_lastPythonRawResponse = [];

if (isNil "CAI_moduleMapIndexers") then { CAI_moduleMapIndexers = []; };
if (isNil "CAI_mapIndexingActive") then { CAI_mapIndexingActive = false; };
if (isNil "CAI_lastMapIndexSummary") then { CAI_lastMapIndexSummary = []; };
if (isNil "CAI_indexDebugMarkers") then { CAI_indexDebugMarkers = []; };
if (isNil "CAI_lastIndexDebugMarkers") then { CAI_lastIndexDebugMarkers = []; };
if (isNil "CAI_moduleWorldModels") then { CAI_moduleWorldModels = []; };
if (isNil "CAI_worldModelActive") then { CAI_worldModelActive = false; };
if (isNil "CAI_lastWorldModelSummary") then { CAI_lastWorldModelSummary = []; };
if (isNil "CAI_worldDebugMarkers") then { CAI_worldDebugMarkers = []; };
if (isNil "CAI_lastWorldDebugMarkers") then { CAI_lastWorldDebugMarkers = []; };

["[CAI CORE]", "Campaign AI core initialized."] call CAI_fnc_log;
