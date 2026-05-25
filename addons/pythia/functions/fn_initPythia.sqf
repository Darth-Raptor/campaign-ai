if (!isServer) exitWith {};

[] spawn {
    sleep 0.1;
    [] call CAI_fnc_checkPythia;
};

