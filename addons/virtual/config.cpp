#include "script_component.hpp"

class CfgPatches {
    class cai_virtual {
        name = "Campaign AI Virtual Forces";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_objectives"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Virtual {
            file = "\x\cai\addons\virtual\functions";
            class initVirtual {};
            class registerVirtualGroup {};
            class collectVirtualForceModules {};
            class applyVirtualOrders {};
            class drawVirtualDebug {};
            class spawnProfile {};
            class despawnProfile {};
        };
    };
};

