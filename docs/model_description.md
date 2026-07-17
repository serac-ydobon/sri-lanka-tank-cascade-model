# Model Description

## Overview

This document is the technical companion to the top-level README. It describes the model architecture and equations.

**Status:** Target architecture is now formally specified (v1.3, below). Implementation covers the single-catchment `Su`/`Sf`/`Ss` stores only (`src/tank_model/hydrology.py`); the `Pond` (tank) compartment and multi-catchment cascade loop are not yet implemented — see "Implementation Status."

## Architecture: Lumped-Catchment Hydrology Model (v1.3)

A **semi-distributed, lumped-catchment water-balance model**: each sub-catchment (= one real tank + its contributing catchment) is internally lumped (whole-catchment average, no internal grid), and sub-catchments are chained in series via a **cascade spillage chain** — upstream `Spill` becomes downstream `Q_in`. Daily timestep. Four storage compartments per sub-catchment:

```
   P (rainfall)
      |
  [alpha partitioning]
    /        \
Qff=a*P   Qinfil=(1-a)*P
   |            |
[Surface       [Vadose Zone (Su)]
 Routing (Sf)]  capacity Su_max
   |            R_vadose = Su/tau_perc  ---\
   |            E_surf (soil evap)          |
   |<--excess--/                            v
   |                                  [Groundwater (Ss)]
   v                                   Qsf = Ss/tau_sf  --> outlet
[Pond (Sp)] <--- Spill from upstream        ^
 frustum geom.                              |
 Spill -> downstream                  R_pond (recharge)
 E_pond (pond evap)  ------------------------/
```

Distinguishing features vs. a plain lumped rainfall-runoff model:
- **Explicit frustum-shaped pond geometry** — this compartment *is* the tank, with dynamic area/depth tracking (not just an abstract mm-depth bucket).
- **Surface-flow routing reservoir** between fast-flow generation and pond inflow.
- **Area-weighted evaporation** split three ways: soil (vadose), pond, and inundated surface.
- **Capacity-limited pond spillage** controlled by a time constant, becoming the next tank's inflow.

Conceptually related to HBV, PDM, FLEX-Topo, and GR4J — comparison in section "Comparison with Established Models" below.

## Implementation Status

| Compartment | Spec | Code | Notes |
|---|---|---|---|
| Vadose Zone (`Su`) | §4.2 | `SU_eq` in `hydrology.py` | Matches spec closely (evaporation not yet area-weighted by `A_eff/A`) |
| Surface Routing (`Sf`) | §4.1 | `SF_eq` in `hydrology.py` | Currently drains to a catchment outlet (`QF`); spec instead drains into the Pond — **needs rewiring** |
| Groundwater (`Ss`) | §4.4 | `SS_eq` in `hydrology.py` | Currently recharged only by vadose percolation `r`; spec adds a second recharge source `R_pond` — **needs extending** |
| α rainfall partitioning | §5 | inline in `toymodel_new_4` | **Verified algebraically identical** to spec's formula: `1-(1-e^-x)/x ≡ (x+e^-x-1)/x` |
| **Pond (`Sp`)** | §4.3, §6 | — | **Not implemented.** Frustum volume/depth/area geometry (cubic solve), pond evaporation, capacity-limited spillage |
| **Multi-catchment cascade** | §3 | — | **Not implemented.** Loop over N sub-catchments, route `Spill_i → Q_in_{i+1}` |
| V-shaped channel inundation | §8 | — | Not implemented (refines `E_flood`; lower priority) |
| **Climate / rainfall generator** | not in v1.3 spec | `climate.py` | Separate concern from the runoff model above — see "Climate / Rainfall Generation Sub-model" |
| Mass balance check | §10 | `hydrology_demo_jaffna.py` (single-catchment version) | Present for the single-catchment case; needs generalizing to multi-catchment `A_total`-weighted form |

## Water Balance Equation (single tank/pond)

```
S_{t+1} = S_t + Inflow_t + Rainfall_t − Evaporation_t − Seepage_t − IrrigationRelease_t − Spill_t
```

| Term | Meaning | Expected units |
|---|---|---|
| `S_t` | Tank (pond) storage at time t | volume (m³) |
| `Inflow_t` | `Qsurf_out` (from Surface Routing) + upstream tank's `Spill` | m³/timestep |
| `Rainfall_t` | Direct rainfall on pond surface | m³/timestep |
| `Evaporation_t` | `E_pond = Ep · A_pond / A` | m³/timestep |
| `Seepage_t` | Pond recharge to groundwater, `R_pond` via `tau_p,sf` | m³/timestep |
| `IrrigationRelease_t` | Controlled release for irrigation (not yet in v1.3 spec — to be added, see `irrigation.py`) | m³/timestep |
| `Spill_t` | `Spill = excess / tau_p,ff` once volume exceeds capacity | m³/timestep |

`Spill_t` from an upstream tank becomes part of `Inflow_{t+1}` for the downstream tank in the cascade.

## Pond Geometry — Inverted Conical Frustum

```
V = (pi*h/3) * (r1^2 + r1*r2 + r2^2)
```
where `r2 = r1 + h/tan(theta)` (`theta` = side slope from horizontal). Given `V_max` and `h_max`, `r1` solved via:
```
r1^2 + r1*delta + (delta^2/3 - 4*V_max/(pi*h_max)) = 0,  delta = h_max/tan(theta)
```
At each step, given current `V`: solve a cubic for current area/depth (see spec §6 for the closed-form root). This is the piece that makes the pond a *real tank* (capacity, water level, surface area all physically consistent) rather than an abstract storage bucket.

## Rainfall Partitioning (α)

```
ir = mir + (ir_max - mir) * (1 - Su/Su_max)
x = P / ir
alpha = (x + exp(-x) - 1) / x   [clamped to 0 <= alpha <= 1]
```
Smoothly transitions from near-zero fast-flow (dry soil) to predominantly fast-flow (wet/saturated soil or intense rain) — analytically expressed Horton-type infiltration excess. **Already implemented** (algebraically equivalent form) in `toymodel_new_4`.

## Evaporation (three-way split, all areas in km²)

| Component | Formula | Drawn from |
|---|---|---|
| Soil (`E_surf`) | `Ep * (Su/Su_max) * (A_eff/A)` | Vadose zone |
| Pond (`E_pond`) | `Ep * A_pond / A` | Pond |
| Inundated (`E_flood`) | `Ep * A_inundated / A` | Surface reservoir (`Sf`) |

`A_eff = A - A_pond - A_inundated`. `E_total = E_surf + E_pond + E_flood`.

## Model Parameters

| Parameter | Symbol | Unit | Description |
|---|---|---|---|
| Catchment Area | `A` | km² | Total sub-catchment surface area |
| Basin Length | `L` | m | V-shaped inundation channel length |
| River Slope | `theta_river` | deg | Longitudinal slope |
| Bank Slope | `theta_bank` | deg | Transverse channel slope |
| Max Pond Volume | `Vp_max` | m³ | Tank capacity |
| Max Pond Height | `hp_max` | m | Max water depth |
| Pond Side Slope | `theta_pond` | deg | Frustum angle from horizontal |
| Fast-flow τ | `tau_ff` | days | Surface routing rate |
| Baseflow τ | `tau_sf` | days | Groundwater rate |
| Pond spill τ | `tau_p,ff` | days | Spillage rate |
| Pond recharge τ | `tau_p,sf` | days | Pond-to-groundwater seepage rate |
| Vadose capacity | `Su_max` | mm | Max soil moisture storage |
| Potential ET | `Ep` | mm/day | Potential evapotranspiration |
| Min infiltration | `mir` | mm/day | Infiltration rate at saturation |
| Max infiltration | `ir_max` | mm/day | Infiltration rate at zero soil moisture |

Derived: `tau_perc = tau_sf` by default (can be split into an independent parameter — see Suggested Improvements). Pond `r1`, `r2`, `A_max` derived from `V_max`, `h_max`, `theta_pond`.

## Comparison with Established Models

| Feature | This Model | HBV | GR4J | PDM | FLEX-Topo |
|---|---|---|---|---|---|
| Storage compartments | 4 | 3 | 2 | 1+ | 3+ |
| Explicit pond geometry | ✓ Frustum | ✗ | ✗ | ✗ | ✗ |
| Surface routing | ✓ Linear | ✓ Triangular | ✓ UH | ✗ | ✓ |
| Multi-catchment cascade | ✓ Spill chain | ✗ | ✗ | ✗ | ✓ |
| Controlled spillage | ✓ `tau_p,ff` | ✗ | ✗ | ✗ | ✗ |
| Area-partitioned ET | ✓ 3-way | Partial | ✗ | ✗ | ✓ |
| α partitioning | Horton analytic | Beta | Ratio | Probability | Threshold |

## Initial Conditions

A wetness factor (0–100%) from the rainfall start month sets initial storages:
```
Su(0) = WetnessFactor * Su_max
Sp(0) = WetnessFactor * Vp_max
Sf(0) = 0, Ss(0) = 0
```

## Climate / Rainfall Generation Sub-model (`climate.py`)

Separate from the runoff-generation sub-model above: instead of taking an observed rainfall record as a fixed given, this generates **synthetic** daily rainfall series with realistic monsoon statistics, for driving Monte Carlo climate-scenario ensembles feeding the eventual optimization layer (Phase 4+). A physical climate model (GCM/RCM) is too expensive to run per-scenario inside an optimization loop (each run needs supercomputer time); this uses a lightweight statistical stochastic weather generator instead.

**Method:** seasonal (per calendar month) first-order Markov chain for wet/dry occurrence + Gamma distribution for rainfall amount on wet days (Richardson 1981-style WGEN). Re-fit separately for each of the 12 calendar months so the model captures Sri Lanka's bimodal Maha/Yala monsoon seasonality, rather than treating rainfall as one stationary process year-round.

- `fit_monthly_markov_gamma(months, rainfall)` — calibrates `P(wet|dry)`, `P(wet|wet)`, and Gamma `(shape, scale)` per month from an observed record, via method-of-moments (`shape = mean²/var`, `scale = var/mean`).
- `simulate_rainfall(n_days, start_date, params)` — walks forward day-by-day, drawing a wet/dry Bernoulli outcome conditioned on the previous day's state and the current calendar month, then a Gamma-distributed amount on wet days.

Published precedent for this exact approach on Sri Lankan dry-zone rainfall (Anuradhapura, Badulla, Hambantota, Katunayake stations) is in `docs/literature_notes.md` — notably, dry-zone stations fit *better* than wet-zone stations with this method, which is favorable for this project's target region.

**Known open items:**
- Calibrated so far only on Jaffna (see Data Requirements below — questionable fit for the target dry-zone tank cascade region).
- Method-of-moments Gamma fit is simpler but less statistically efficient than MLE; acceptable for now, MLE is a possible future refinement.
- Does not yet model spatial correlation of rainfall across multiple sub-catchments in a cascade (each catchment would currently need independent calibration/simulation) — relevant once the multi-catchment cascade loop exists.
- Does not detect/handle date gaps in the input record when fitting transition probabilities (documented limitation, not yet enforced in code).

## Data Requirements

To move from the single-catchment toy model to a real tank-cascade instance, four categories of data are needed:

1. **Rainfall & evaporation time series** (daily, per sub-catchment) — `P` and `Ep`.
2. **Tank/pond geometry** — `Vp_max`, `hp_max`, `theta_pond` (or equivalently a surveyed storage-area-depth curve, which is more reliable than assuming a perfect frustum).
3. **Catchment/channel physical parameters** — `A`, `L`, `theta_river`, `theta_bank`, plus the time constants (`tau_ff`, `tau_sf`, `tau_p,ff`, `tau_p,sf`) and infiltration parameters (`Su_max`, `mir`, `ir_max`), which are typically *calibrated* against observed data rather than measured directly.
4. **Cascade topology** — how many tanks, their upstream/downstream connectivity, and (ideally) each tank's catchment boundary.
5. **Calibration/validation target** (optional but needed for anything beyond a synthetic demo) — observed tank storage, water level, or outflow records.

**Status of the Jaffna/Iranaimadu dataset** (`notebooks/hydrology_demo_jaffna.py`): covers only item 1, and only partially — it has real daily rainfall (1975–2025) but `Ep` is currently a placeholder constant, not real data. It has none of items 2–5. It's also geographically a questionable fit: Jaffna peninsula is limestone/coral karst terrain, hydrologically distinct from the dry-zone tank cascade regions (Anuradhapura/Kurunegala/Polonnaruwa) covered in `docs/literature_notes.md`, and Iranamadu is a single large reservoir rather than a documented multi-tank cascade — so it's useful as a rainfall-input source and for exercising the runoff code, but not as the demo cascade site itself.

**Better candidate for a first real (non-synthetic) demo:** the **Thirappane cascade** (Jayatilaka et al. 2003, in `docs/literature_notes.md`) — it already has published, field-calibrated values for items 2 and 3 (four tanks: Vendarankulama, Bulankulama, Meegassagama, Alisthana) and a real cascade topology (item 4), since that paper's model is this project's direct precedent. Real tank storage/outflow observations (item 5) would need to come from that paper's underlying dataset or a fresh field survey — not confirmed available yet.

## Open Questions / Design Decisions

- Timestep: daily vs. sub-daily? (v1.3 spec assumes daily.)
- Should `tau_perc` (vadose percolation) be split from `tau_sf` (baseflow) as an independent calibratable parameter (see Suggested Improvements)?
- First real demo cascade: synthetic 3–5 tank network, or seeded with Thirappane's published parameters?
- Calibration framework not yet chosen (see Suggested Improvements — SCE-UA or DDS against NSE/KGE).

## Suggested Improvements (from v1.3 spec, not yet actioned)

1. Separate `tau_perc` parameter, independent of `tau_sf`.
2. Spatially variable rainfall (2D rainfall array infrastructure exists in spec but untested).
3. Snow module — not relevant for Sri Lanka, skip.
4. Interception storage (canopy bucket before rainfall reaches ground).
5. Seasonally varying `Ep` (currently constant; link to temperature/radiation).
6. Groundwater routing *between* catchments (currently only surface/pond spill connects them).
7. Calibration framework (SCE-UA or DDS, objective functions NSE/KGE).
8. Sensitivity analysis (Monte Carlo or Morris screening).
9. Pond evaporation limiter — cap `E_pond` at available pond volume.
10. Non-linear groundwater reservoir (`Qsf = k·Ss^b`) for flexible baseflow recession.

## References

Model design references (from v1.3 spec):
- Bergström, S. (1976). Development and application of a conceptual runoff model for Scandinavian catchments. *SMHI Reports RHO 7*.
- Perrin, C., Michel, C., & Andréassian, V. (2003). Improvement of a parsimonious model for streamflow simulation. *J. Hydrology*, 279, 275–289.
- Moore, R. J. (2007). The PDM rainfall-runoff model. *HESS*, 11(1), 483–499.
- Savenije, H. H. G. (2010). HESS Opinions: Topography driven conceptual modelling (FLEX-Topo). *HESS*, 14, 2681–2692.
- Fenicia, F., Kavetski, D., & Savenije, H. H. G. (2011). Elements of a flexible approach for conceptual hydrological modeling. *WRR*, 47, W11510.

Sri Lanka tank cascade domain references: see `docs/literature_notes.md`.
