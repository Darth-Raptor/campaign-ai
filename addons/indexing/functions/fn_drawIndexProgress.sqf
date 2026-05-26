params [
    ["_center", [0, 0, 0], [[]]],
    ["_cellCount", 0, [0]],
    ["_worldSize", worldSize, [0]],
    ["_cellSize", 500, [0]]
];

private _marker = "CAI_INDEX_PROGRESS";
private _cellsPerSide = ceil (_worldSize / _cellSize);
private _totalCells = _cellsPerSide * _cellsPerSide;

deleteMarker _marker;
createMarker [_marker, _center];
_marker setMarkerShape "ICON";
_marker setMarkerType "mil_dot";
_marker setMarkerColor "ColorYellow";
_marker setMarkerText format ["CAI INDEX %1/%2", _cellCount, _totalCells];

CAI_indexDebugMarkers pushBackUnique _marker;
true

