#include "script_component.hpp"

class CfgPatches {
    class cai_modules {
        name = "Campaign AI Eden Modules";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_world", "A3_Modules_F"};
        units[] = {
            "CAI_ModuleMapIndexer",
            "CAI_ModuleWorldModel"
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
            class moduleMapIndexer {};
            class moduleWorldModel {};
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
            class Slider: Default {
                control = "Slider";
                typeName = "NUMBER";
            };
        };
        class ModuleDescription;
    };

    class CAI_ModuleMapIndexer: Module_F {
        scope = 2;
        scopeCurator = 0;
        displayName = "Campaign AI Map Indexer";
        category = "CAI_Modules";
        function = "CAI_fnc_moduleMapIndexer";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;

        class Attributes: AttributesBase {
            class CAI_autoStart: Checkbox {
                property = "CAI_autoStart";
                displayName = "Auto Start";
                tooltip = "Automatically starts map indexing when the mission begins in single-player/editor preview.";
                defaultValue = "true";
                expression = "_this setVariable ['CAI_autoStart', _value, true];";
            };
            class CAI_forceReindex: Checkbox {
                property = "CAI_forceReindex";
                displayName = "Force Reindex";
                tooltip = "Ignores an existing compatible JSON index and scans the map again.";
                defaultValue = "false";
                expression = "_this setVariable ['CAI_forceReindex', _value, true];";
            };
            class CAI_cellSize: Edit {
                property = "CAI_cellSize";
                displayName = "Cell Size";
                tooltip = "Terrain grid cell size in meters. Larger values index faster; smaller values produce more detail.";
                defaultValue = "500";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_cellSize', _caiValue, true];";
            };
            class CAI_roadScanRadius: Edit {
                property = "CAI_roadScanRadius";
                displayName = "Road Scan Radius";
                tooltip = "Road search radius around each terrain grid cell center, in meters.";
                defaultValue = "350";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_roadScanRadius', _caiValue, true];";
            };
            class CAI_objectScanRadius: Edit {
                property = "CAI_objectScanRadius";
                displayName = "Object Scan Radius";
                tooltip = "Tactical site and structure search radius around each terrain grid cell center, in meters.";
                defaultValue = "300";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; _this setVariable ['CAI_objectScanRadius', _caiValue, true];";
            };
            class CAI_outputFile: Edit {
                property = "CAI_outputFile";
                displayName = "Output File";
                tooltip = "Mission-relative JSON output path. The default writes campaign_ai\\map_index.json inside the unpacked mission folder.";
                defaultValue = """campaign_ai\map_index.json""";
                expression = "_this setVariable ['CAI_outputFile', _value, true];";
            };
            class CAI_debugMarkers: Checkbox {
                property = "CAI_debugMarkers";
                displayName = "Debug Markers";
                tooltip = "Shows a temporary map marker indicating indexing progress.";
                defaultValue = "true";
                expression = "_this setVariable ['CAI_debugMarkers', _value, true];";
            };
            class CAI_debugMarkerMode: Combo {
                property = "CAI_debugMarkerMode";
                displayName = "Debug Marker Mode";
                tooltip = "Choose which runtime-important derived map index markers appear after indexing completes.";
                defaultValue = """OBJECTIVES""";
                expression = "_this setVariable ['CAI_debugMarkerMode', _value, true];";
                class Values {
                    class OBJECTIVES {
                        name = "Objectives Only";
                        value = "OBJECTIVES";
                        default = 1;
                    };
                    class OBJECTIVES_CONTEXT {
                        name = "Objectives + Context";
                        value = "OBJECTIVES_CONTEXT";
                    };
                };
            };
            class ModuleDescription: ModuleDescription {};
        };
    };

    class CAI_ModuleWorldModel: Module_F {
        scope = 2;
        scopeCurator = 0;
        displayName = "Campaign AI World Model";
        category = "CAI_Modules";
        function = "CAI_fnc_moduleWorldModel";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;

        class Attributes: AttributesBase {
            class CAI_autoStart: Checkbox {
                property = "CAI_worldAutoStart";
                displayName = "Auto Start";
                tooltip = "Automatically loads the completed Campaign AI map index and seeds the runtime world model at mission start.";
                defaultValue = "true";
                expression = "_this setVariable ['CAI_autoStart', _value, true];";
            };
            class CAI_mapIndexFile: Edit {
                property = "CAI_mapIndexFile";
                displayName = "Map Index File";
                tooltip = "Mission-relative path to the schema-2 Campaign AI map index JSON.";
                defaultValue = """campaign_ai\map_index.json""";
                expression = "_this setVariable ['CAI_mapIndexFile', _value, true];";
            };
            class CAI_objectiveDensity: Combo {
                property = "CAI_objectiveDensity";
                displayName = "Objective Density";
                tooltip = "Controls the map-scaled target count for seeded runtime objectives.";
                defaultValue = """BALANCED""";
                expression = "_this setVariable ['CAI_objectiveDensity', _value, true];";
                class Values {
                    class SPARSE {
                        name = "Sparse";
                        value = "SPARSE";
                    };
                    class BALANCED {
                        name = "Balanced";
                        value = "BALANCED";
                        default = 1;
                    };
                    class DENSE {
                        name = "Dense";
                        value = "DENSE";
                    };
                };
            };
            class CAI_minimumScore: Slider {
                property = "CAI_minimumScore";
                displayName = "Minimum Score";
                tooltip = "Lowest map-index objective candidate score allowed into runtime objective seeding.";
                defaultValue = "0.4";
                typeName = "NUMBER";
                expression = "private _caiValue = if (_value isEqualType 0) then {_value} else {private _caiText = if (_value isEqualType '') then {_value} else {str _value}; parseNumber _caiText}; if (_caiValue <= 1) then {_caiValue = _caiValue * 100}; _this setVariable ['CAI_minimumScore', ((_caiValue max 0) min 100), true];";
                class Values {
                    min = 0;
                    max = 1;
                    step = 0.01;
                };
            };
            class CAI_debugMarkers: Checkbox {
                property = "CAI_worldDebugMarkers";
                displayName = "Debug Markers";
                tooltip = "Draws map markers for the actual seeded runtime objectives.";
                defaultValue = "true";
                expression = "_this setVariable ['CAI_debugMarkers', _value, true];";
            };
            class ModuleDescription: ModuleDescription {};
        };
    };
};
