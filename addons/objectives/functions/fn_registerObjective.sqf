params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith { false };

if !(_logic in CAI_moduleObjectives) then {
    CAI_moduleObjectives pushBack _logic;
};

true

