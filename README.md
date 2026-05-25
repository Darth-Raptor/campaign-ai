# Campaign AI

Campaign AI is an Arma 3 operational campaign simulation mod. It uses Pythia to run Python-owned campaign state and SQF-owned Arma validation/application logic.

## V1.0 Scope

V1.0 targets the handoff MVP:

- Server-authoritative Campaign AI execution.
- Required Pythia bridge with safe disable behavior.
- Python-owned objective, commander, virtual group, intel, combat, and persistence state.
- SQF validation for Python responses, commander orders, combat results, and server authority.
- Eden modules for objectives, commanders, virtual forces, and debug.
- Local JSON snapshot save/load.
- Debug logs and marker-ready debug snapshots.
- Predictable conventional commander recommendations.
- Low-frequency virtual movement.
- Offscreen virtual combat resolution.

V1.0 does not include backend sync, Discord/SIGACT/logistics integrations, client-side Python, arbitrary Python execution, full Zeus command tooling, full spawned AI lifecycle, ALiVE-style map indexing, or per-frame Python simulation.

## Required Dependency

Load order:

```text
-mod=@Pythia;@Campaign_AI
```

Pythia must be available on the dedicated server. If Pythia is missing or returns invalid data, Campaign AI disables itself and the mission continues.

## Source Layout

```text
addons/
  core/
  pythia/
  objectives/
  virtual/
  intel/
  combat/
  commanders/
  modules/
python_code/
  $PYTHIA$
  __init__.py
  api.py
  state.py
  ...
tools/
  build.ps1
  pack.ps1
tests/
```

## Python API Contract

All SQF calls go through `CAI_fnc_pyCall`.

Every Python API returns:

```python
[success, statusCode, payload, logs]
```

Required V1.0 calls:

- `CAIPython.api.ping`
- `CAIPython.api.init_state`
- `CAIPython.api.get_state_summary`
- `CAIPython.api.save_snapshot`
- `CAIPython.api.load_snapshot`
- `CAIPython.api.get_debug_snapshot`
- `CAIPython.api.commander_cycle`
- `CAIPython.api.resolve_combat_batch`

## Local Python Tests

```powershell
python -m unittest discover -s tests
```

The tests load `python_code` the same way Pythia does: the package name is read from `python_code/$PYTHIA$`.

## Build/Staging

Stage the public mod folder:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build.ps1
```

Package addon PBOs when a supported packer is available:

```powershell
powershell -ExecutionPolicy Bypass -File tools/pack.ps1
```

`pack.ps1` auto-detects HEMTT, Mikero `pboProject`, Arma 3 Tools `FileBank.exe`, or Arma 3 Tools `AddonBuilder.exe`. If none is installed, it stages unpacked addon source for inspection and logs that PBO packaging still needs to be run on a machine with an Arma packer.

## V1.0 Test Plan

The three-phase QA plan lives at:

```text
docs/testing/three_phase_test_plan.md
```

Standard smoke-test fixture:

```text
missions/CAI_V1_SmokeTest.VR
```

Run preflight before listen-server testing:

```powershell
powershell -ExecutionPolicy Bypass -File tools/test_preflight.ps1
```

Create a phase test log:

```powershell
powershell -ExecutionPolicy Bypass -File tools/new_test_log.ps1 -Phase Phase1-Listen
```

Stage the mission and mod into a local dedicated server root:

```powershell
powershell -ExecutionPolicy Bypass -File tools/stage_test_assets.ps1 -TargetRoot "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Server"
```

Start the local dedicated smoke-test server:

```powershell
powershell -ExecutionPolicy Bypass -File tools/start_local_dedicated.ps1
```

Create a HostHavoc upload bundle:

```powershell
powershell -ExecutionPolicy Bypass -File tools/create_hosthavoc_package.ps1
```

The HostHavoc bundle contains a staged `@Campaign_AI` folder and, when Arma 3 Tools `FileBank.exe` is available, `MPMissions\CAI_V1_SmokeTest.VR.pbo`.

## HostHavoc Validation Checklist

1. Upload `@Pythia` and `@Campaign_AI`.
2. Start the dedicated server with `-mod=@Pythia;@Campaign_AI -autoInit`.
3. Confirm RPT logs `[CAI CORE] Campaign AI core initialized.`
4. Confirm `[CAI PYTHIA] Ping successful. Package: CAIPython.`
5. Confirm sample or Eden state initializes through Python.
6. Confirm JSON save/load logs a state summary.
7. Confirm the mission continues if Pythia is removed or blocked.
8. Confirm commander cycles and virtual combat do not run while systems are disabled.
