#include "script_component.hpp"

class CfgPatches {
    class cai_indexing {
        name = "Campaign AI Map Indexing";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_pythia"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Indexing {
            file = "\x\cai\addons\indexing\functions";
            class initIndexing { postInit = 1; };
            class collectIndexBatch {};
            class collectMapLocations {};
            class collectRoadsAtPosition {};
            class collectTacticalSitesAtPosition {};
            class collectTerrainCell {};
            class drawIndexProgress {};
            class drawIndexDebugMarkers {};
            class registerMapIndexer {};
            class scanMapIndex {};
            class sendIndexBatch {};
            class showMapIndexDebug {};
            class startMapIndex {};
        };
    };
};
