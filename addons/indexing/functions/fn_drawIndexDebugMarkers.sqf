params [
    ["_markers", [], [[]]]
];

{
    deleteMarker _x;
} forEach CAI_indexDebugMarkers;
CAI_indexDebugMarkers = [];

{
    private _markerId = [_x, "markerId", format ["CAI_IDX_%1", _forEachIndex]] call CAI_fnc_getKV;
    private _position = [_x, "position", [0, 0, 0]] call CAI_fnc_getKV;
    private _markerType = [_x, "markerType", "mil_dot"] call CAI_fnc_getKV;
    private _markerColor = [_x, "markerColor", "ColorWhite"] call CAI_fnc_getKV;
    private _markerText = [_x, "markerText", "CAI INDEX"] call CAI_fnc_getKV;

    deleteMarker _markerId;
    createMarker [_markerId, _position];
    _markerId setMarkerShape "ICON";
    _markerId setMarkerType _markerType;
    _markerId setMarkerColor _markerColor;
    _markerId setMarkerText _markerText;
    _markerId setMarkerSize [0.8, 0.8];
    CAI_indexDebugMarkers pushBackUnique _markerId;
} forEach _markers;

true
