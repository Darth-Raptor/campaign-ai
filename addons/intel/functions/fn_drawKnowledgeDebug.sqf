params [
    ["_snapshot", CAI_lastDebugSnapshot, [[]]]
];

private _knowledge = [_snapshot, "knowledge", []] call CAI_fnc_getKV;

{
    private _commanderId = [_x, "commanderId", "cmd"] call CAI_fnc_getKV;
    private _contacts = [_x, "contacts", []] call CAI_fnc_getKV;
    if (_contacts isEqualType createHashMap) then { _contacts = values _contacts; };
    {
        private _contactId = [_x, "contactId", "contact"] call CAI_fnc_getKV;
        private _position = [_x, "position", [0, 0, 0]] call CAI_fnc_getKV;
        private _confidence = [_x, "confidence", 0] call CAI_fnc_getKV;
        private _marker = format ["CAI_KNOW_%1_%2", _commanderId, _contactId];

        deleteMarker _marker;
        createMarker [_marker, _position];
        _marker setMarkerShape "ICON";
        _marker setMarkerType "mil_unknown";
        _marker setMarkerColor "ColorOrange";
        _marker setMarkerText format ["%1 contact %2 | %3", _commanderId, _contactId, _confidence];
        CAI_debugMarkers pushBackUnique _marker;
    } forEach _contacts;
} forEach _knowledge;

true

