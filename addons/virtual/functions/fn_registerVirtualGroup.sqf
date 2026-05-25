params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith { false };

if !(_logic in CAI_moduleVirtualForces) then {
    CAI_moduleVirtualForces pushBack _logic;
};

true

