private _customObjectives = [];
CAI_customObjectiveMirror = createHashMap;

if (isNil "CAI_moduleCustomObjectives") then { CAI_moduleCustomObjectives = []; };

{
    if (!isNull _x) then {
        private _index = _forEachIndex + 1;
        private _customObjectiveId = format ["custom_%1", _index];
        private _name = _x getVariable ["CAI_objectiveName", ""];
        if (_name isEqualTo "") then {
            _name = format ["Custom Objective %1", _index];
        };

        private _radiusRaw = _x getVariable ["CAI_objectiveRadius", 300];
        private _radiusValue = if (_radiusRaw isEqualType 0) then {
            _radiusRaw
        } else {
            private _radiusText = if (_radiusRaw isEqualType "") then {_radiusRaw} else {str _radiusRaw};
            parseNumber _radiusText
        };
        if (_radiusValue <= 1) then { _radiusValue = 100 + (_radiusValue * 900); };
        private _radius = round ((_radiusValue max 100) min 1000);

        private _entry = [
            ["customObjectiveId", _customObjectiveId],
            ["name", _name],
            ["objectiveType", _x getVariable ["CAI_objectiveType", "other"]],
            ["objectiveDescription", _x getVariable ["CAI_objectiveDescription", "other"]],
            ["radius", _radius],
            ["initialOwner", _x getVariable ["CAI_initialOwner", "NONE"]],
            ["significance", _x getVariable ["CAI_significance", "MEDIUM"]],
            ["position", getPosATL _x]
        ];

        _customObjectives pushBack _entry;
        CAI_customObjectiveMirror set [_customObjectiveId, _entry];
    };
} forEach CAI_moduleCustomObjectives;

["[CAI WORLD]", format ["Collected %1 custom objective module(s).", count _customObjectives]] call CAI_fnc_log;
_customObjectives

