#include "script_component.hpp"

class CfgPatches {
    class cai_core {
        name = "Campaign AI Core";
        author = "Campaign AI";
        requiredVersion = 2.10;
        requiredAddons[] = {"A3_Functions_F"};
        units[] = {};
        weapons[] = {};
    };
};

class CfgFunctions {
    class CAI {
        class Core {
            file = "\x\cai\addons\core\functions";
            class initCore { postInit = 1; };
            class log {};
            class isServerAuthority {};
            class getTime {};
            class disableSystems {};
            class getKV {};
            class toHashMap {};
        };
    };
};

