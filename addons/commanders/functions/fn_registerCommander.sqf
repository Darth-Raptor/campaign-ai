params [
    ["_logic", objNull, [objNull]]
];

if (!isServer || {isNull _logic}) exitWith { false };

if !(_logic in CAI_moduleCommanders) then {
    CAI_moduleCommanders pushBack _logic;
};

true

