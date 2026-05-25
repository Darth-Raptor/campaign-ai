player createDiarySubject ["CAI_Test", "Campaign AI Test"];
player createDiaryRecord [
    "CAI_Test",
    [
        "Smoke Test",
        "Use this mission for Campaign AI V1.0 listen-server, local dedicated, and HostHavoc validation. The fixture is centered around grid 050050. Open the map after startup and verify CAI debug markers for objectives, virtual groups, commander HQ, movement updates, and the Phase 7 combat report in RPT."
    ]
];

player createDiaryRecord [
    "CAI_Test",
    [
        "Phase 7 Combat",
        "The server automatically triggers one offscreen combat check about 8 seconds after Campaign AI initializes. Expected RPT lines include [CAI TEST] Phase 7 combat smoke response and [CAI COMBAT] Combat result accepted. To test the safety skip, move within 1000m of the combat cluster near grid 052050 and run [(missionNamespace getVariable ['CAI_TEST_phase7CombatEngagement', []]), false, 'NONE'] call CAI_fnc_requestCombatResolution; from the server debug console."
    ]
];

hint "Campaign AI V1.0 Phase 7 test bed loaded. Open the map and watch the centered CAI debug markers.";
