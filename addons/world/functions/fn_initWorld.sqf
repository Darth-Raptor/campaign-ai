if (!isServer) exitWith {};

if (isNil "CAI_moduleWorldModels") then { CAI_moduleWorldModels = []; };
if (isNil "CAI_worldModelActive") then { CAI_worldModelActive = false; };
if (isNil "CAI_lastWorldModelSummary") then { CAI_lastWorldModelSummary = []; };
if (isNil "CAI_worldDebugMarkers") then { CAI_worldDebugMarkers = []; };
if (isNil "CAI_lastWorldDebugMarkers") then { CAI_lastWorldDebugMarkers = []; };
if (isNil "CAI_moduleCustomObjectives") then { CAI_moduleCustomObjectives = []; };
if (isNil "CAI_customObjectiveMirror") then { CAI_customObjectiveMirror = createHashMap; };

["[CAI WORLD]", "Runtime world model subsystem ready."] call CAI_fnc_log;
