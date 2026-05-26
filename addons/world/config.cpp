#include "script_component.hpp"

class CfgPatches {
    class cai_world {
        name = "Campaign AI World Model";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_indexing"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class World {
            file = "\x\cai\addons\world\functions";
            class collectCustomObjectiveModules {};
            class drawWorldDebugMarkers {};
            class initWorld { postInit = 1; };
            class initWorldModel {};
            class registerCustomObjective {};
            class registerWorldModel {};
            class showWorldDebug {};
            class startWorldModel {};
        };
    };
};
