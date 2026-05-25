#include "script_component.hpp"

class CfgPatches {
    class cai_modules {
        name = "Campaign AI Eden Modules";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_commanders", "A3_Modules_F"};
        units[] = {
            "CAI_ModuleObjective",
            "CAI_ModuleCommander",
            "CAI_ModuleVirtualForces",
            "CAI_ModuleDebug"
        };
        weapons[] = {};
    };
};

class CfgFactionClasses {
    class CAI_Modules {
        displayName = "Campaign AI";
        priority = 2;
        side = 7;
    };
};

class CfgFunctions {
    class CAI {
        class Modules {
            file = "\x\cai\addons\modules\functions";
            class initModules { postInit = 1; };
            class moduleObjective {};
            class moduleVirtualForces {};
            class moduleCommander {};
            class moduleDebug {};
        };
    };
};

class CfgVehicles {
    class Logic;
    class Module_F: Logic {
        class AttributesBase {
            class Default;
            class Edit;
            class Combo;
            class Checkbox;
        };
        class ModuleDescription;
    };

    class CAI_ModuleObjective: Module_F {
        scope = 2;
        scopeCurator = 0;
        displayName = "Campaign AI Objective";
        category = "CAI_Modules";
        function = "CAI_fnc_moduleObjective";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;

        class Attributes: AttributesBase {
            class CAI_objectiveId: Edit {
                property = "CAI_objectiveId";
                displayName = "Objective ID";
                tooltip = "Unique Campaign AI objective id.";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_objectiveId', _value, true];";
            };
            class CAI_objectiveName: Edit {
                property = "CAI_objectiveName";
                displayName = "Objective Name";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_objectiveName', _value, true];";
            };
            class CAI_objectiveType: Edit {
                property = "CAI_objectiveType";
                displayName = "Objective Type";
                defaultValue = """generic""";
                expression = "_this setVariable ['CAI_objectiveType', _value, true];";
            };
            class CAI_initialOwner: Combo {
                property = "CAI_initialOwner";
                displayName = "Initial Owner";
                defaultValue = """UNKNOWN""";
                expression = "_this setVariable ['CAI_initialOwner', _value, true];";
                class Values {
                    class UNKNOWN { name = "UNKNOWN"; value = "UNKNOWN"; default = 1; };
                    class WEST { name = "WEST"; value = "WEST"; };
                    class EAST { name = "EAST"; value = "EAST"; };
                    class GUER { name = "GUER"; value = "GUER"; };
                };
            };
            class CAI_priority: Edit {
                property = "CAI_priority";
                displayName = "Priority";
                defaultValue = "50";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_priority', _caiValue, true];";
            };
            class CAI_radius: Edit {
                property = "CAI_radius";
                displayName = "Radius";
                defaultValue = "300";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_radius', _caiValue, true];";
            };
            class CAI_size: Edit {
                property = "CAI_size";
                displayName = "Size";
                defaultValue = """medium""";
                expression = "_this setVariable ['CAI_size', _value, true];";
            };
            class CAI_terrainType: Edit {
                property = "CAI_terrainType";
                displayName = "Terrain Type";
                defaultValue = """mixed""";
                expression = "_this setVariable ['CAI_terrainType', _value, true];";
            };
            class CAI_garrisonSlots: Edit {
                property = "CAI_garrisonSlots";
                displayName = "Garrison Slots";
                defaultValue = "0";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_garrisonSlots', _caiValue, true];";
            };
            class CAI_debugEnabled: Checkbox {
                property = "CAI_debugEnabled";
                displayName = "Debug Enabled";
                defaultValue = "false";
                expression = "_this setVariable ['CAI_debugEnabled', _value, true];";
            };
            class ModuleDescription: ModuleDescription {};
        };
    };

    class CAI_ModuleCommander: Module_F {
        scope = 2;
        scopeCurator = 0;
        displayName = "Campaign AI Commander";
        category = "CAI_Modules";
        function = "CAI_fnc_moduleCommander";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;

        class Attributes: AttributesBase {
            class CAI_commanderId: Edit {
                property = "CAI_commanderId";
                displayName = "Commander ID";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_commanderId', _value, true];";
            };
            class CAI_commanderName: Edit {
                property = "CAI_commanderName";
                displayName = "Commander Name";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_commanderName', _value, true];";
            };
            class CAI_side: Combo {
                property = "CAI_side";
                displayName = "Side";
                defaultValue = """EAST""";
                expression = "_this setVariable ['CAI_side', _value, true];";
                class Values {
                    class EAST { name = "EAST"; value = "EAST"; default = 1; };
                    class WEST { name = "WEST"; value = "WEST"; };
                    class GUER { name = "GUER"; value = "GUER"; };
                };
            };
            class CAI_faction: Edit {
                property = "CAI_faction";
                displayName = "Faction";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_faction', _value, true];";
            };
            class CAI_commanderType: Edit {
                property = "CAI_commanderType";
                displayName = "Commander Type";
                defaultValue = """conventional""";
                expression = "_this setVariable ['CAI_commanderType', _value, true];";
            };
            class CAI_posture: Combo {
                property = "CAI_posture";
                displayName = "Posture";
                defaultValue = """BALANCED""";
                expression = "_this setVariable ['CAI_posture', _value, true];";
                class Values {
                    class BALANCED { name = "BALANCED"; value = "BALANCED"; default = 1; };
                    class DEFENSIVE { name = "DEFENSIVE"; value = "DEFENSIVE"; };
                    class AGGRESSIVE { name = "AGGRESSIVE"; value = "AGGRESSIVE"; };
                };
            };
            class CAI_aoMarker: Edit {
                property = "CAI_aoMarker";
                displayName = "AO Marker";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_aoMarker', _value, true];";
            };
            class CAI_cycleTime: Edit {
                property = "CAI_cycleTime";
                displayName = "Cycle Time";
                defaultValue = "120";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_cycleTime', _caiValue, true];";
            };
            class CAI_aggression: Edit {
                property = "CAI_aggression";
                displayName = "Aggression";
                defaultValue = "50";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_aggression', _caiValue, true];";
            };
            class CAI_reservePercentage: Edit {
                property = "CAI_reservePercentage";
                displayName = "Reserve Percentage";
                defaultValue = "20";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_reservePercentage', _caiValue, true];";
            };
            class CAI_attackThreshold: Edit {
                property = "CAI_attackThreshold";
                displayName = "Attack Threshold";
                defaultValue = "1.25";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_attackThreshold', _caiValue, true];";
            };
            class CAI_reinforcementThreshold: Edit {
                property = "CAI_reinforcementThreshold";
                displayName = "Reinforcement Threshold";
                defaultValue = "60";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_reinforcementThreshold', _caiValue, true];";
            };
            class CAI_debugEnabled: Checkbox {
                property = "CAI_debugEnabled";
                displayName = "Debug Enabled";
                defaultValue = "false";
                expression = "_this setVariable ['CAI_debugEnabled', _value, true];";
            };
            class CAI_persistenceEnabled: Checkbox {
                property = "CAI_persistenceEnabled";
                displayName = "Persistence Enabled";
                defaultValue = "true";
                expression = "_this setVariable ['CAI_persistenceEnabled', _value, true];";
            };
            class ModuleDescription: ModuleDescription {};
        };
    };

    class CAI_ModuleVirtualForces: Module_F {
        scope = 2;
        scopeCurator = 0;
        displayName = "Campaign AI Virtual Forces";
        category = "CAI_Modules";
        function = "CAI_fnc_moduleVirtualForces";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;

        class Attributes: AttributesBase {
            class CAI_groupId: Edit {
                property = "CAI_groupId";
                displayName = "Group ID";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_groupId', _value, true];";
            };
            class CAI_side: Combo {
                property = "CAI_side";
                displayName = "Side";
                defaultValue = """EAST""";
                expression = "_this setVariable ['CAI_side', _value, true];";
                class Values {
                    class EAST { name = "EAST"; value = "EAST"; default = 1; };
                    class WEST { name = "WEST"; value = "WEST"; };
                    class GUER { name = "GUER"; value = "GUER"; };
                };
            };
            class CAI_faction: Edit {
                property = "CAI_faction";
                displayName = "Faction";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_faction', _value, true];";
            };
            class CAI_commanderId: Edit {
                property = "CAI_commanderId";
                displayName = "Commander ID";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_commanderId', _value, true];";
            };
            class CAI_forceSize: Combo {
                property = "CAI_forceSize";
                displayName = "Force Size";
                defaultValue = """platoon""";
                expression = "_this setVariable ['CAI_forceSize', _value, true];";
                class Values {
                    class platoon { name = "Platoon"; value = "platoon"; default = 1; };
                    class company { name = "Company"; value = "company"; };
                    class battalion { name = "Battalion"; value = "battalion"; };
                };
            };
            class CAI_unitType: Edit {
                property = "CAI_unitType";
                displayName = "Unit Type";
                defaultValue = """infantry""";
                expression = "_this setVariable ['CAI_unitType', _value, true];";
            };
            class CAI_mobility: Combo {
                property = "CAI_mobility";
                displayName = "Mobility";
                defaultValue = """foot""";
                expression = "_this setVariable ['CAI_mobility', _value, true];";
                class Values {
                    class foot { name = "Foot"; value = "foot"; default = 1; };
                    class motorized { name = "Motorized"; value = "motorized"; };
                    class mechanized { name = "Mechanized"; value = "mechanized"; };
                    class armor { name = "Armor"; value = "armor"; };
                    class static { name = "Static"; value = "static"; };
                };
            };
            class CAI_initialObjective: Edit {
                property = "CAI_initialObjective";
                displayName = "Initial Objective";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_initialObjective', _value, true];";
            };
            class CAI_debugEnabled: Checkbox {
                property = "CAI_debugEnabled";
                displayName = "Debug Enabled";
                defaultValue = "false";
                expression = "_this setVariable ['CAI_debugEnabled', _value, true];";
            };
            class ModuleDescription: ModuleDescription {};
        };
    };

    class CAI_ModuleDebug: Module_F {
        scope = 2;
        scopeCurator = 0;
        displayName = "Campaign AI Debug";
        category = "CAI_Modules";
        function = "CAI_fnc_moduleDebug";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;

        class Attributes: AttributesBase {
            class CAI_enableDebug: Checkbox {
                property = "CAI_enableDebug";
                displayName = "Enable Debug";
                defaultValue = "false";
                expression = "_this setVariable ['CAI_enableDebug', _value, true];";
            };
            class CAI_debugMode: Combo {
                property = "CAI_debugMode";
                displayName = "Debug Mode";
                defaultValue = """BOTH""";
                expression = "_this setVariable ['CAI_debugMode', _value, true];";
                class Values {
                    class TRUE_STATE { name = "True State"; value = "TRUE_STATE"; };
                    class COMMANDER_KNOWLEDGE { name = "Commander Knowledge"; value = "COMMANDER_KNOWLEDGE"; };
                    class BOTH { name = "Both"; value = "BOTH"; default = 1; };
                };
            };
            class CAI_commanderFilter: Edit {
                property = "CAI_commanderFilter";
                displayName = "Commander ID Filter";
                defaultValue = """""";
                expression = "_this setVariable ['CAI_commanderFilter', _value, true];";
            };
            class CAI_markerRefreshInterval: Edit {
                property = "CAI_markerRefreshInterval";
                displayName = "Marker Refresh Interval";
                defaultValue = "30";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_markerRefreshInterval', _caiValue, true];";
            };
            class ModuleDescription: ModuleDescription {};
        };
    };
};
