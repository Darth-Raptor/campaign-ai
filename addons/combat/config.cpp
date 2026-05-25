#include "script_component.hpp"

class CfgPatches {
    class cai_combat {
        name = "Campaign AI Combat";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_intel"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Combat {
            file = "\x\cai\addons\combat\functions";
            class initCombat {};
            class detectCombatEngagements {};
            class resolveCombatEngagementPosition {};
            class validateCombatEngagement {};
            class requestCombatResolution {};
            class validateCombatResult {};
            class applyCombatResult {};
            class drawCombatDebug {};
        };
    };
};
