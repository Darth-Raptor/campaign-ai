params [
    ["_center", [0, 0, 0], [[]]],
    ["_radius", 350, [0]]
];

private _roads = _center nearRoads _radius;
private _results = [];

{
    private _road = _x;
    private _position = getPosATL _road;
    private _roadId = format ["road_%1_%2", round ((_position select 0) * 10), round ((_position select 1) * 10)];
    private _connectedIds = [];
    {
        private _connectedPosition = getPosATL _x;
        _connectedIds pushBackUnique format ["road_%1_%2", round ((_connectedPosition select 0) * 10), round ((_connectedPosition select 1) * 10)];
    } forEach (roadsConnectedTo [_road, true]);

    _results pushBack [
        ["roadId", _roadId],
        ["position", _position],
        ["roadInfo", getRoadInfo _road],
        ["connectedRoadIds", _connectedIds],
        ["source", "nearRoads"]
    ];
} forEach _roads;

_results

