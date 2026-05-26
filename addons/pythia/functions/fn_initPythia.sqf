if (!isServer) exitWith {};

[] spawn {
    sleep 0.25;
    [] call CAI_fnc_checkPythia;
};

