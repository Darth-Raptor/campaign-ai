params [
    ["_center", [0, 0, 0], [[]]],
    ["_radius", 300, [0]]
];

private _types = [
    "BUNKER",
    "FORTRESS",
    "FUELSTATION",
    "HOSPITAL",
    "TRANSMITTER",
    "VIEW-TOWER",
    "WATERTOWER",
    "POWER LINES",
    "POWERSOLAR",
    "POWERWIND",
    "POWERWAVE",
    "RAILWAY",
    "QUAY",
    "CHURCH",
    "CHAPEL",
    "LIGHTHOUSE",
    "SHIPWRECK"
];

private _results = [];

{
    private _siteType = _x;
    private _objects = nearestTerrainObjects [_center, [_siteType], _radius, false, true];
    {
        private _position = getPosATL _x;
        _results pushBack [
            ["siteId", format ["site_%1_%2_%3", _siteType, round ((_position select 0) * 10), round ((_position select 1) * 10)]],
            ["type", _siteType],
            ["position", _position],
            ["confidence", 1],
            ["source", "nearestTerrainObjects"]
        ];
    } forEach _objects;
} forEach _types;

_results

