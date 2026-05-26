private _worldSize = worldSize;
private _center = [_worldSize / 2, _worldSize / 2, 0];
private _radius = (sqrt 2) * (_worldSize / 2);
private _types = [
    "NameCityCapital",
    "NameCity",
    "NameVillage",
    "NameLocal",
    "Airport",
    "Hill",
    "Mount",
    "Strategic",
    "StrongpointArea",
    "FlatArea",
    "FlatAreaCity",
    "FlatAreaCitySmall",
    "CityCenter",
    "BorderCrossing",
    "o_installation",
    "b_installation",
    "n_installation",
    "u_installation",
    "o_hq",
    "b_hq",
    "n_hq",
    "o_air",
    "b_air",
    "n_air",
    "o_naval",
    "b_naval",
    "n_naval"
];

private _locations = nearestLocations [_center, _types, _radius, _center];
private _seen = createHashMap;
private _results = [];

{
    private _position = locationPosition _x;
    private _locationType = type _x;
    private _name = text _x;
    private _key = format ["%1_%2_%3", _locationType, round (_position select 0), round (_position select 1)];

    if !(_key in _seen) then {
        _seen set [_key, true];
        _results pushBack [
            ["locationId", format ["loc_%1", count _results + 1]],
            ["name", _name],
            ["type", _locationType],
            ["position", _position],
            ["category", if (_locationType in ["NameCityCapital", "NameCity", "NameVillage", "CityCenter"]) then {"settlement"} else {"terrain"}],
            ["source", "nearestLocations"]
        ];
    };
} forEach _locations;

["[CAI INDEX]", format ["Collected %1 map location(s).", count _results]] call CAI_fnc_log;
_results

