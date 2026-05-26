params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith { false };

if (isNil "CAI_moduleMapIndexers") then { CAI_moduleMapIndexers = []; };
if (isNil "CAI_mapIndexingActive") then { CAI_mapIndexingActive = false; };
if (isNil "CAI_lastMapIndexSummary") then { CAI_lastMapIndexSummary = []; };
if (isNil "CAI_indexDebugMarkers") then { CAI_indexDebugMarkers = []; };
if (isNil "CAI_lastIndexDebugMarkers") then { CAI_lastIndexDebugMarkers = []; };

if !(_logic in CAI_moduleMapIndexers) then {
    CAI_moduleMapIndexers pushBack _logic;
};

if (_logic getVariable ["CAI_autoStart", true]) then {
    [_logic] spawn {
        params ["_indexer"];
        sleep 1;
        [_indexer] call CAI_fnc_startMapIndex;
    };
};

["[CAI INDEX]", "Map Indexer module registered."] call CAI_fnc_log;
true
