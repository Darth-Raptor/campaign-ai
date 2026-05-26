params [
    ["_markers", [], [[]]]
];

if (isNil "CAI_worldDebugMarkers") then { CAI_worldDebugMarkers = []; };

{
    deleteMarker _x;
} forEach CAI_worldDebugMarkers;
CAI_worldDebugMarkers = [];

{
    private _markerId = [_x, "markerId", format ["CAI_WORLD_%1", _forEachIndex]] call CAI_fnc_getKV;
    private _position = [_x, "position", [0, 0, 0]] call CAI_fnc_getKV;
    private _markerType = [_x, "markerType", "mil_objective"] call CAI_fnc_getKV;
    private _markerColor = [_x, "markerColor", "ColorGreen"] call CAI_fnc_getKV;
    private _markerText = [_x, "markerText", "CAI WORLD OBJ"] call CAI_fnc_getKV;

    deleteMarker _markerId;
    createMarker [_markerId, _position];
    _markerId setMarkerShape "ICON";
    _markerId setMarkerType _markerType;
    _markerId setMarkerColor _markerColor;
    _markerId setMarkerText _markerText;
    _markerId setMarkerSize [0.9, 0.9];
    CAI_worldDebugMarkers pushBackUnique _markerId;
} forEach _markers;

true
