# Campaign AI

Campaign AI is an Arma 3 operational campaign simulation mod. This `Core` branch starts from a clean implementation while preserving the established Campaign AI identity:

- Public mod folder: `@Campaign_AI`
- Addon prefix: `cai`
- SQF function tag: `CAI`
- Python package name: `CAIPython`
- Required dependency: `@Pythia`

## Core Branch Focus

The first Core feature is the `Campaign AI Map Indexer` Eden module. A mission maker places one player unit and the module, previews the mission in single player, and Campaign AI scans the map into a portable JSON file in the mission folder.

The second Core feature is the `Campaign AI World Model` Eden module. It reads a completed schema-2 map index, seeds Python-owned neutral runtime objectives with map-scaled score-and-spread selection, and can draw debug markers for the actual seeded objectives.

Mission makers can also place `Campaign AI Custom Objective` modules. Custom objectives are seeded before index-derived objectives, suppress nearby derived duplicates, and preserve mission-maker ownership/significance metadata for future commander systems. Airfield custom objectives use a wider runtime support footprint so nearby towers and support sites are treated as part of the airfield instead of separate objectives. Runtime world-model seeding also groups overlapping derived candidates so compact compounds are represented by one objective marker.

## Load Order

```text
-mod=@Pythia;@Campaign_AI
```

## Python API Contract

All SQF calls go through `CAI_fnc_pyCall`. Every Python API returns:

```python
[success, statusCode, payload, logs]
```

## Build

```powershell
powershell -ExecutionPolicy Bypass -File tools\build.ps1
powershell -ExecutionPolicy Bypass -File tools\pack.ps1
```

## Tests

```powershell
python -m unittest discover -s tests
powershell -ExecutionPolicy Bypass -File tools\test_preflight.ps1
```
