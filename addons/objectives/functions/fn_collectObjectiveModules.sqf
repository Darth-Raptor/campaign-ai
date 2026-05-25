private _objectives = [];
CAI_objectiveMirror = createHashMap;

{
    private _index = _forEachIndex + 1;
    private _defaultId = format ["obj_%1", _index toFixed 0];
    private _objectiveId = _x getVariable ["CAI_objectiveId", _defaultId];
    if (_objectiveId isEqualTo "") then { _objectiveId = _defaultId; };

    private _entry = [
        ["objectiveId", _objectiveId],
        ["name", _x getVariable ["CAI_objectiveName", _objectiveId]],
        ["objectiveType", _x getVariable ["CAI_objectiveType", "generic"]],
        ["initialOwner", _x getVariable ["CAI_initialOwner", "UNKNOWN"]],
        ["owner", _x getVariable ["CAI_initialOwner", "UNKNOWN"]],
        ["control", _x getVariable ["CAI_control", 100]],
        ["priority", _x getVariable ["CAI_priority", 50]],
        ["radius", _x getVariable ["CAI_radius", 300]],
        ["size", _x getVariable ["CAI_size", "medium"]],
        ["terrainType", _x getVariable ["CAI_terrainType", "mixed"]],
        ["garrisonSlots", _x getVariable ["CAI_garrisonSlots", 0]],
        ["position", getPosATL _x],
        ["debugEnabled", _x getVariable ["CAI_debugEnabled", false]]
    ];

    _objectives pushBack _entry;
    CAI_objectiveMirror set [_objectiveId, _entry];
} forEach CAI_moduleObjectives;

["[CAI OBJ]", format ["Collected %1 objective module(s).", count _objectives]] call CAI_fnc_log;
_objectives
