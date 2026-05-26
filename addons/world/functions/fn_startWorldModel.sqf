params [
    ["_logic", objNull, [objNull]]
];

if (!isServer) exitWith { false };
if (isNull _logic) exitWith {
    ["[CAI WORLD]", "World model cannot start because the module logic is null."] call CAI_fnc_log;
    false
};
if (isNil "CAI_worldModelActive") then { CAI_worldModelActive = false; };
if (CAI_worldModelActive) exitWith {
    ["[CAI WORLD]", "World model initialization is already running."] call CAI_fnc_log;
    false
};

CAI_worldModelActive = true;
[_logic] spawn CAI_fnc_initWorldModel;
true
