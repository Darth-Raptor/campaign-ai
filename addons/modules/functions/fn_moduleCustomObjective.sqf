private _logic = param [0, objNull, [objNull]];
private _activated = if ((count _this) > 2) then {
    param [2, true, [true]]
} else {
    param [1, true, [true]]
};

if (!_activated) exitWith {};
[_logic] call CAI_fnc_registerCustomObjective;

