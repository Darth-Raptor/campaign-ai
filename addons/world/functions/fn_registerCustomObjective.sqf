params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith { false };

if (isNil "CAI_moduleCustomObjectives") then { CAI_moduleCustomObjectives = []; };
if (isNil "CAI_customObjectiveMirror") then { CAI_customObjectiveMirror = createHashMap; };

if !(_logic in CAI_moduleCustomObjectives) then {
    CAI_moduleCustomObjectives pushBack _logic;
};

["[CAI WORLD]", "Custom Objective module registered."] call CAI_fnc_log;
true

