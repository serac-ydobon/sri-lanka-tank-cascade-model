# Model Description

## Overview

This document is the technical companion to the top-level README. It describes the intended model architecture and equations. **Status: design only — no implementation yet.**

## Architecture Overview

- **Node** = a single tank, with state variable `S` (storage volume).
- **Edge** = a spill/release pathway routed as inflow to the downstream tank.
- Planned module breakdown (mirrors `src/tank_model/`):
  - `single_tank.py` — single-tank water balance
  - `cascade_network.py` — graph/topology and routing between tanks
  - `hydrology.py` — rainfall, evaporation, and seepage estimation
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
