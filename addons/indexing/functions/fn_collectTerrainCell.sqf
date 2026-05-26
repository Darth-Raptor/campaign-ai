params [
    ["_center", [0, 0, 0], [[]]],
    ["_cellSize", 500, [0]],
    ["_roadScanRadius", 350, [0]],
    ["_objectScanRadius", 300, [0]]
];

private _x = _center select 0;
private _y = _center select 1;
private _sample = (_cellSize / 4) max 25;
private _height = getTerrainHeightASL [_x, _y];
private _eastHeight = getTerrainHeightASL [(_x + _sample) min worldSize, _y];
private _northHeight = getTerrainHeightASL [_x, (_y + _sample) min worldSize];
private _slopeEstimate = ((abs (_height - _eastHeight)) + (abs (_height - _northHeight))) / (2 * _sample);
private _roadCount = count (_center nearRoads _roadScanRadius);
private _structureCount = count (nearestTerrainObjects [_center, ["BUILDING", "HOUSE"], _objectScanRadius, false, true]);
private _isWater = surfaceIsWater [_x, _y];
private _surface = surfaceType [_x, _y];
private _category = "open";

if (_isWater) then {
    _category = "water";
} else {
    if (_structureCount > 4) then {
        _category = "urban";
    } else {
        if (_roadCount > 2) then {
            _category = "roadside";
        } else {
            if (_slopeEstimate > 0.2) then {
                _category = "rough";
            };
        };
    };
};

[
    ["cellId", format ["cell_%1_%2", round _x, round _y]],
    ["center", _center],
    ["cellSize", _cellSize],
    ["heightASL", _height],
    ["surfaceType", _surface],
    ["isWater", _isWater],
    ["slopeEstimate", _slopeEstimate],
    ["roadDensity", _roadCount],
    ["structureDensity", _structureCount],
    ["terrainCategory", _category]
]

