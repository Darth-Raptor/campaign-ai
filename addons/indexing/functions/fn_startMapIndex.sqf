params [
    ["_logic", objNull, [objNull]]
];

if (!isServer) exitWith { false };
if (isNull _logic) exitWith {
    ["[CAI INDEX]", "Map indexing cannot start because the module logic is null."] call CAI_fnc_log;
    false
};
if (CAI_mapIndexingActive) exitWith {
    ["[CAI INDEX]", "Map indexing is already running."] call CAI_fnc_log;
    false
};

CAI_mapIndexingActive = true;
[_logic] spawn CAI_fnc_scanMapIndex;
true

