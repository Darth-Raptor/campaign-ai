params [
    ["_logic", objNull, [objNull]],
    ["_activated", true, [true]]
];

if (!_activated) exitWith {};
[_logic] call CAI_fnc_registerVirtualGroup;

