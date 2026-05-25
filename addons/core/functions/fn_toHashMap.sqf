params [
    ["_container", [], [[], createHashMap]]
];

if (_container isEqualType createHashMap) exitWith { _container };

private _map = createHashMap;
{
    if ((_x isEqualType []) && {(count _x) >= 2}) then {
        _map set [_x select 0, _x select 1];
    };
} forEach _container;

_map

