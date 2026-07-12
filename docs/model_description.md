# Model Description

## Overview

This document is the technical companion to the top-level README. It describes the intended model architecture and equations. **Status: design only — no implementation yet.**

## Architecture Overview

- **Node** = a single tank, with state variable `S` (storage volume).
- **Edge** = a spill/release pathway routed as inflow to the downstream tank.
- Planned module breakdown (mirrors `src/tank_model/`):
  - `single_tank.py` — single-tank water balance
  - `cascade_network.py` — graph/topology and routing between tanks
  - `hydrology.py` — **initial implementation exists.** A three-store conceptual rainfall-runoff model (unsaturated zone / fast surface reservoir / slow groundwater reservoir, with a saturation-excess nonlinear infiltration function and a groundwater pumping/abstraction term). Generates catchment runoff (`QT`, mm/timestep) intended as the upstream input to a tank's `Inflow_t` — see "Runoff Generation Sub-model" below.
  - `irrigation.py` — demand and release rules
  - `optimization.py` — future optimization layer (see README Roadmap)

## Water Balance Equation

For each tank, at each timestep:

```
S_{t+1} = S_t + Inflow_t + Rainfall_t − Evaporation_t − Seepage_t − IrrigationRelease_t − Spill_t
```

| Term | Meaning | Expected units |
|---|---|---|
| `S_t` | Tank storage at time t | volume (e.g. m³ or Mm³) |
| `Inflow_t` | Catchment runoff + upstream tank spill/release | volume / timestep |
| `Rainfall_t` | Direct rainfall on tank surface | volume / timestep |
| `Evaporation_t` | Evaporation from tank surface | volume / timestep |
| `Seepage_t` | Seepage/percolation loss | volume / timestep |
| `IrrigationRelease_t` | Controlled release for irrigation | volume / timestep |
| `Spill_t` | Overflow once `S_t` exceeds capacity | volume / timestep |

Timestep is expected to be daily (TBD — see Open Questions). `Spill_t` from an upstream tank becomes part of `Inflow_{t+1}` for the downstream tank in the cascade.

## Runoff Generation Sub-model (`hydrology.py`)

A three-store conceptual model (`toymodel_new_4`, ported from a standalone script) generates catchment runoff to feed `Inflow_t`:

- **Unsaturated zone reservoir (`Su`)** — nonlinear saturation-excess infiltration function (Xinanjiang/PDM-style): the split between quickflow and infiltration (`alpha`) varies with current soil moisture relative to capacity `Su_max`. Overflow past `Su_max` splits into a groundwater fraction (`beta`) and a fast-reservoir fraction (`1-beta`). Evaporation scales with relative soil moisture, capped at potential ET.
- **Slow-response reservoir (`Ss`)** — linear groundwater reservoir (time constant `Ts`) with a groundwater pumping/abstraction term (capped by availability) representing agro-well irrigation demand.
- **Fast-response reservoir (`Sf`)** — linear surface reservoir (time constant `Tf`) receiving direct quickflow plus the fast-reservoir overflow fraction.
- Output `QT = QF + QS` (mm/timestep) is catchment runoff depth — **must be converted to volume (× catchment area) before use as a tank's `Inflow_t`.**

**Known open items (not yet resolved):**
- `Ep` (potential evaporation) is currently a placeholder constant — should be replaced with real per-basin/per-land-cover values (see Bastiaanssen & Chandrapala 2003 in `docs/literature_notes.md`).
- Parameters (`mir`, `Su_max`, `Ts`, `Tf`, `beta`) are hand-picked, not calibrated against observed streamflow — unlike the Jayatilaka et al. (2003) precedent model, which was field-calibrated.
- `beta = 1.0` in the current demo run routes 100% of saturation-excess overflow to groundwater and 0% to the fast reservoir's overflow input — worth double-checking this is intentional.
- No unit-conversion helper yet from mm/timestep (catchment depth) to m³/timestep (tank inflow volume).

## Processes To Be Modeled

- **Rainfall input** — data source TBD (met station or gridded product).
- **Evaporation** — pan evaporation or Penman-based estimate, TBD.
- **Seepage** — simple loss coefficient vs. a more physical model, TBD.
- **Irrigation release** — rule-based, driven by cropping calendar/demand, TBD.
- **Spill/overflow routing** — connects upstream and downstream cascade nodes.

## Open Questions / Design Decisions

- Timestep: daily vs. sub-daily?
- Calibration data availability (observed storage/outflow records)?
- Number of tanks in the first demo cascade (synthetic 3–5 tank network planned)?
