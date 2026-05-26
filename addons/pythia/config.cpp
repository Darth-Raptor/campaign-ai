#include "script_component.hpp"

class CfgPatches {
    class cai_pythia {
        name = "Campaign AI Pythia Bridge";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"cai_core"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Pythia {
            file = "\x\cai\addons\pythia\functions";
            class initPythia { postInit = 1; };
            class checkPythia {};
            class pyCall {};
            class pyPing {};
        };
    };
};

