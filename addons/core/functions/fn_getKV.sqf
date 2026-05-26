params [
    ["_container", [], [[], createHashMap]],
    ["_key", "", [""]],
    ["_default", nil]
];

if (_container isEqualType createHashMap) exitWith {
    _container getOrDefault [_key, _default]
};

private _result = _default;
{
    if ((_x isEqualType []) && {(count _x) >= 2} && {(_x select 0) isEqualTo _key}) exitWith {
        _result = _x select 1;
    };
} forEach _container;

_result

