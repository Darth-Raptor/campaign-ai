# Campaign AI V1.0 Three-Phase Test Plan

This plan validates Campaign AI V1.0 in three escalating environments:

1. Local listen server.
2. Local dedicated server.
3. HostHavoc dedicated server.

Use the same mission fixture for every phase: `missions/CAI_V1_SmokeTest.VR`.

## Shared Preflight

Run before Phase 1 and again after any code change:

```powershell
powershell -ExecutionPolicy Bypass -File tools/test_preflight.ps1
```

Preflight must pass:

- Python API unit tests.
- `@Campaign_AI` staging and PBO packaging.
- Required PBO names exist.
- PBO prefix and SQF function contents are verifiable when Arma 3 Tools `BankRev.exe` is installed.

## Phase 1: Local Listen Server

Goal: prove fast local multiplayer startup before dedicated server complexity.

Use Arma client multiplayer hosting with:

```text
-mod=@Pythia;@Campaign_AI
```

Run mission:

```text
CAI_V1_SmokeTest.VR
```

Pass checks:

- Mission loads without addon/config errors.
- RPT includes `[CAI CORE] Campaign AI core initialized.`
- RPT includes `[CAI PYTHIA] Ping successful. Package: CAIPython.`
- RPT includes `Initial Pythia save/load proof path completed.`
- Map shows CAI objective, virtual group, and commander markers.
- Server console/manual debug can run `["red_cmd_01"] call CAI_fnc_commanderCycle;`.
- Failure run without `@Pythia` logs a clear disable reason and the mission remains playable.

Exit gate: Pythia ping, state init, JSON save/load, debug markers, commander cycle, and safe-disable all pass.

## Phase 2: Local Dedicated Server

Goal: prove server/client separation and local dedicated packaging.

Stage the mission and mod into the local server root:

```powershell
powershell -ExecutionPolicy Bypass -File tools/stage_test_assets.ps1 -TargetRoot "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Server"
```

Start the local dedicated server:

```powershell
powershell -ExecutionPolicy Bypass -File tools/start_local_dedicated.ps1
```

Pass checks:

- Server starts with `-mod=@Pythia;@Campaign_AI`.
- Client can join without client-side Python calls.
- Server RPT shows core init, Pythia ping, state init, JSON save/load, and commander cycle logs.
- Client RPT does not show Python command-decision execution.
- Debug markers are visible to the joined client.
- Offscreen combat resolves when manually triggered away from players.
- Combat is skipped when a player is near the engagement position.
- Failure run without `@Pythia` leaves the mission joinable and logs safe-disable.

Exit gate: all Phase 1 behavior works on a true dedicated server/client split.

## Phase 3: HostHavoc Dedicated Server

Goal: validate the real deployment target.

Deploy:

- `@Pythia`
- staged `@Campaign_AI`
- `MPMissions\CAI_V1_SmokeTest.VR.pbo`

Create a HostHavoc upload bundle:

```powershell
powershell -ExecutionPolicy Bypass -File tools/create_hosthavoc_package.ps1
```

Use modline:

```text
-mod=@Pythia;@Campaign_AI -autoInit
```

Pass checks:

- HostHavoc boots with both mods loaded.
- RPT shows Pythia availability and `CAIPython.api.ping` success.
- Python requirements are available or confirmed unnecessary for this smoke path.
- JSON save folder is writable.
- Eden/module-compatible fixture state initializes into Python.
- Save/load proof path completes.
- Commander scheduler runs server-side every 120 seconds.
- Debug snapshot/markers are usable for admin oversight.
- Offscreen combat resolves only when no players are near.
- Failure run with Pythia unavailable disables Campaign AI and leaves the mission running.

Exit gate: HostHavoc passes the same smoke path as local dedicated, including persistence write/read and safe failure behavior.

## Manual Server Exec Snippets

Run a commander cycle:

```sqf
["red_cmd_01"] call CAI_fnc_commanderCycle;
```

Request debug snapshot:

```sqf
[[["debugMode", "BOTH"], ["commanderId", ""], ["gameTime", serverTime]]] call CAI_fnc_pyGetDebugSnapshot;
```

Trigger offscreen combat:

```sqf
private _engagement = [
    ["position", [1200, 0, 0]],
    ["objectiveId", "obj_blue_outpost"],
    ["attackerGroupId", "grp_red_001"],
    ["defenderGroupId", "grp_blue_001"]
];
[[_engagement], false] call CAI_fnc_requestCombatResolution;
```

Trigger near-player combat skip by moving a player within 1000 meters of `[1200, 0, 0]`, then running the same combat snippet.
