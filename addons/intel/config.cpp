#include "script_component.hpp"

class CfgPatches {
    class cai_intel {
        name = "Campaign AI Intel";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_virtual"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Intel {
            file = "\x\cai\addons\intel\functions";
            class initIntel {};
            class collectObservedEvents {};
            class drawKnowledgeDebug {};
        };
    };
};

