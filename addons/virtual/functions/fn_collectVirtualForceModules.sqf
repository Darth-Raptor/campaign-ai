private _groups = [];
CAI_virtualGroupMirror = createHashMap;

{
    private _index = _forEachIndex + 1;
    private _defaultId = format ["grp_%1", _index toFixed 0];
    private _groupId = _x getVariable ["CAI_groupId", _defaultId];
    if (_groupId isEqualTo "") then { _groupId = _defaultId; };

    private _entry = [
        ["groupId", _groupId],
        ["name", _x getVariable ["CAI_groupName", _groupId]],
        ["side", _x getVariable ["CAI_side", "EAST"]],
        ["faction", _x getVariable ["CAI_faction", ""]],
        ["commanderId", _x getVariable ["CAI_commanderId", ""]],
        ["forceSize", _x getVariable ["CAI_forceSize", "platoon"]],
        ["unitType", _x getVariable ["CAI_unitType", "infantry"]],
        ["mobility", _x getVariable ["CAI_mobility", "foot"]],
        ["position", getPosATL _x],
        ["initialObjective", _x getVariable ["CAI_initialObjective", ""]],
        ["debugEnabled", _x getVariable ["CAI_debugEnabled", false]],
        ["manualOverride", false]
    ];

    _groups pushBack _entry;
    CAI_virtualGroupMirror set [_groupId, _entry];
} forEach CAI_moduleVirtualForces;

["[CAI VIRTUAL]", format ["Collected %1 virtual force module(s).", count _groups]] call CAI_fnc_log;
_groups

