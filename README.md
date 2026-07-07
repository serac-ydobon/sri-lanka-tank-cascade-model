# Sri Lanka Tank Cascade Model

A network-based hydrological simulation of traditional Sri Lankan tank cascade irrigation systems.

## Project Status

Early-stage — Phase 1: repository scaffolding only, no model code yet. Actively developed summer 2026; check back for updates.

## Motivation

Traditional tank cascade systems are centuries-old, decentralized irrigation networks in Sri Lanka's dry zone. Understanding cascade-level water dynamics matters for drought resilience, water security, and preserving a functioning heritage system.

The ultimate research goal is to **optimize agricultural economic output** from a tank cascade system, as a function of several interacting factors:

1. **Climate** — monsoon rainfall patterns
2. **Hydrology** — rainfall → riverflow / groundwater
3. **Reservoir cascade dynamics** — storage, spill, and transfer between tanks
4. **Agriculture** — irrigation area → crop production → economic output
5. **Population** — water demand

Most existing hydrological studies model tanks in isolation. This project instead models the cascade as a connected network, as a foundation for eventually optimizing toward that economic-output goal.

## Background: Tank Cascade Systems

A "tank cascade" is a chain of small reservoirs (tanks) connected so that spill/overflow from an upstream tank becomes inflow to the next tank downstream. Each tank serves local irrigation and has its own catchment, storage capacity, and community management. See [docs/literature_notes.md](docs/literature_notes.md) for supporting sources.

## Model Purpose & Scope (Summer 2026)

The goal for this phase is to build a working **simulation** of tank water balance and cascade connectivity — **not optimization yet**:

1. Single-tank water balance model
2. Multi-tank cascade network (upstream spill/release → downstream inflow)

Optimization toward the economic-output goal (e.g. LP/DP/GA/RL for irrigation reliability and drought resilience) is future work — see Roadmap below.

## Planned Architecture

- **Node-link network**: each real tank is a node with its own state (storage); edges represent spill/release routed to downstream tanks.
- Modular design (not yet implemented): `src/tank_model/{single_tank, cascade_network, hydrology, irrigation, optimization}.py`
- Config-driven cascade definitions (`configs/*.yaml`) planned so cascades can be specified without code changes.

```
Tank A → Tank B → Tank C   (diagram to be added)
```

## Water Balance Equation

Core state update per tank per timestep:

```
S_{t+1} = S_t + Inflow_t + Rainfall_t − Evaporation_t − Seepage_t − IrrigationRelease_t − Spill_t
```

Where `S` = storage, `Inflow` = catchment runoff plus upstream spill/release, `Rainfall`/`Evaporation` act directly on the tank surface, `Seepage` is loss to groundwater, `IrrigationRelease` is controlled outflow, and `Spill` is overflow once capacity is exceeded. Full details in [docs/model_description.md](docs/model_description.md).

## Repository Structure

```
data/            raw and processed datasets
notebooks/       exploratory analysis and demo notebooks
src/tank_model/  model source code
configs/         cascade topology and parameter YAML configs
results/         generated figures and simulation outputs
docs/            model description and literature notes
tests/           unit tests
```

## Getting Started

No installable code yet — setup instructions will be added once model code exists.

- Single-tank demo: coming soon (`notebooks/single_tank_demo.ipynb`)
- Cascade demo: coming soon (`notebooks/cascade_simulation_demo.ipynb`)

## Roadmap

- **Phase 1 (now)**: repository scaffolding, literature review
- **Phase 2**: single-tank water balance model + demo notebook
- **Phase 3**: cascade network model (multi-tank) + demo notebook
- **Phase 4+**: optimization layer targeting agricultural economic output, incorporating climate, hydrology, agriculture, and population factors
