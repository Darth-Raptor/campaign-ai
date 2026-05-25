#include "script_component.hpp"

class CfgPatches {
    class cai_commanders {
        name = "Campaign AI Commanders";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_combat"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Commanders {
            file = "\x\cai\addons\commanders\functions";
            class initCommanders {};
            class registerCommander {};
            class collectCommanderModules {};
            class startCommanderScheduler {};
            class commanderCycle {};
            class validateRecommendedOrders {};
            class applyRecommendedOrders {};
            class pauseCommander {};
            class resumeCommander {};
            class drawCommanderDebug {};
        };
    };
};

