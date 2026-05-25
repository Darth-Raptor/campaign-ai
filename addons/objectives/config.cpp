#include "script_component.hpp"

class CfgPatches {
    class cai_objectives {
        name = "Campaign AI Objectives";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_pythia"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Objectives {
            file = "\x\cai\addons\objectives\functions";
            class initObjectives {};
            class registerObjective {};
            class collectObjectiveModules {};
            class drawObjectiveDebug {};
        };
    };
};

