params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith { false };

if (isNil "CAI_moduleWorldModels") then { CAI_moduleWorldModels = []; };
if (isNil "CAI_worldModelActive") then { CAI_worldModelActive = false; };
if (isNil "CAI_lastWorldModelSummary") then { CAI_lastWorldModelSummary = []; };
if (isNil "CAI_worldDebugMarkers") then { CAI_worldDebugMarkers = []; };
if (isNil "CAI_lastWorldDebugMarkers") then { CAI_lastWorldDebugMarkers = []; };

if !(_logic in CAI_moduleWorldModels) then {
    CAI_moduleWorldModels pushBack _logic;
};

if (_logic getVariable ["CAI_autoStart", true]) then {
    [_logic] spawn {
        params ["_worldModel"];
        sleep 1.5;
        [_worldModel] call CAI_fnc_startWorldModel;
    };
};

["[CAI WORLD]", "World Model module registered."] call CAI_fnc_log;
true

