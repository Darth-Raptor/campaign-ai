if (!isServer) exitWith {};

if (isNil "CAI_moduleMapIndexers") then { CAI_moduleMapIndexers = []; };
if (isNil "CAI_mapIndexingActive") then { CAI_mapIndexingActive = false; };
if (isNil "CAI_lastMapIndexSummary") then { CAI_lastMapIndexSummary = []; };
if (isNil "CAI_indexDebugMarkers") then { CAI_indexDebugMarkers = []; };
if (isNil "CAI_lastIndexDebugMarkers") then { CAI_lastIndexDebugMarkers = []; };

["[CAI INDEX]", "Map indexing subsystem ready."] call CAI_fnc_log;
