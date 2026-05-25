params [
    ["_orders", [], [[]]]
];

[_orders] call CAI_fnc_applyVirtualOrders;

{
    private _orderId = [_x, "orderId", ""] call CAI_fnc_getKV;
    private _orderType = [_x, "orderType", ""] call CAI_fnc_getKV;
    private _groupId = [_x, "groupId", ""] call CAI_fnc_getKV;
    ["[CAI CMD]", format ["Accepted order %1. %2 -> %3.", _orderId, _groupId, _orderType]] call CAI_fnc_log;
} forEach _orders;

true

