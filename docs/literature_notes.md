# Literature Notes

## Purpose

Running list of literature reviewed for this project. Supports the Motivation/Background sections of the top-level README. Source PDFs live locally at `Desktop/Tank Cascade Sri Lanka India/` (see Storage Note below — not committed to this repo).

## Core Model Precedent

### Jayatilaka, Sakthivadivel, Shinogi, Makin & Witharana (2003)
*"A simple water balance modelling approach for determining water availability in an irrigation tank cascade system."* Journal of Hydrology, 273, 81–102.

**The direct precedent for this project's model.** Presents "Cascade," a node-link daily water-balance model calibrated on four tanks (Vendarankulama, Bulankulama, Meegassagama, Alisthana) of the six-tank Thirappane cascade near Anuradhapura (21 months of field data, Jul 1997–Apr 1999). Tank types: ST (start), NT (normal, one upstream inflow), CT (confluence, multiple upstream inflows) — directly maps onto this project's node-link cascade design.

Water balance structure matches our `S_{t+1} = S_t + Inflow_t + Rainfall_t − Evaporation_t − Seepage_t − IrrigationRelease_t − Spill_t` equation, with specific functional forms worth reusing:
- **Inflow** = rainfall runoff (modified Antecedent Precipitation Index runoff-coefficient method) + rain-on-tank + return flow (seepage/spill) from upstream tank
- **Evaporation** = pan evaporation × pan coefficient (fp = 0.8)
- **Seepage/percolation** = log function of relative tank water height (calibrated per tank) — **dominant loss term**: 42–84% of total inflow
- **Spillway discharge** = broad-crested weir formula (discharge coefficient fd = 1.7)
- Return-flow coefficient fr = 0.10; spill-transfer coefficient fs = 0.5

Other component shares: rainfall runoff = 60–85% of inflow; rain-on-tank 15–17% (head tanks) vs 25–26% (tail tanks); evaporation 8–23% of inflow; irrigation release only 4–22% of inflow; spillway discharge 3–5%. Study-area rainfall ~1490 mm/yr, potential ET 2453 mm/yr.

**Relevance:** Hydrology + cascade dynamics. Use as the template for `hydrology.py` / `single_tank.py` equations and as a source of realistic calibrated parameter ranges for a synthetic demo cascade.

## Hydrology Inputs (Evaporation, Rainfall, Water Balance)

### Bastiaanssen & Chandrapala (2003)
*"Water balance variability across Sri Lanka for assessing agricultural and environmental water use."* Agricultural Water Management, 58, 171–192.

Island-wide actual evapotranspiration at 1 km resolution via SEBAL (satellite energy balance) on NOAA-AVHRR imagery, closed against rainfall (400+ gauges) with a "rest term" explicitly attributed in part to Sri Lanka's ~18,387 tanks. Full water balance table for all 103 river basins (rainfall, ET, runoff, runoff coefficient per basin) — a reusable empirical dataset.

Key numbers: national avg. rainfall 1751 mm/yr, national ET 1279 mm/yr; ET by land cover ranges 1226 mm/yr (paddy) to 1407 mm/yr (dry monsoon forest); SEBAL validated against scintillometer at Horana (17% error at 10-day, 1% at monthly). Runoff coefficients per basin 0.08–0.67. Padawiya tank (Anuradhapura) has the highest recorded open-water evaporation (1889 mm/yr). National water accounting: irrigation uses only 7% of net inflow.

**Relevance:** Directly informs the `Evaporation_t` term — validated methodology and per-basin/per-land-cover rates usable for parameterizing or validating the model.

## Cascade Network Topology

### Jayasena, Chandrajith & Gangadhara (2011)
*"Water Management in Ancient Tank Cascade Systems (TCS) in Sri Lanka: Evidence for Systematic Tank Distribution."* Journal of the Geological Society of Sri Lanka, 14, 29–34.

Studies the spatial/hierarchical structure of 4,633 small tanks across 25 cascades in the Deduru Oya basin (Kurunegala District — highest tank density in Sri Lanka, ~1 tank/1.2 km²). Defines a "tank sequence number" (headwater = 1, increasing downstream); tank count per sequence follows log-linear decay. Introduces "Degree of Cascading" (DOC = 10^−slope), ranging 1.6 (dry, flat terrain, 1200–1300 mm/yr rainfall) to 4.5 (wetter, gentler slopes, 1800–1900 mm/yr); regression R² typically >0.97.

**Relevance:** Gives an empirical basis for realistic cascade size/branching as a function of local rainfall regime — useful for designing the synthetic demo cascade's topology. Named cascades (Deduru Oya basin): Dorabawatta, Kadawalagedara, Hittarapola, Pannitawa, Baladora, Bogoda, Malagane, Thambarawa, Nelliya, Karagaswewa, Bayawa.

## Drought Resilience / Socio-hydrology — Traditional vs. Modern System Comparison

> **★ Key comparison for this project:** both papers below study the *same* Mahaweli System H irrigation area, contrasting a **modern centralized canal** against a **traditional tank-cascade-buffered canal** fed by the same reservoir. This is the clearest evidence in the literature set that tank cascades measurably outperform modern systems on drought resilience — directly motivates the project's premise.

| | New Jaya Ganga (NJG) — modern | Yoda Ela (YE) — traditional, tank-buffered |
|---|---|---|
| Built | Modern era | 459 AD (King Dhatusena) |
| Command area | 14,017 ha | 4,721 ha |
| Canal length | 46 km | 28 km |
| Conveyance efficiency | 60% | 70% |
| Reservoir-water dependency | 18% higher than YE | baseline |
| Rainfall-threshold dependency | 12% higher than YE | baseline |
| Water-duty increment in drought years | **58.3%** | **16.4%** (≈3.5× less water-stress amplification) |

### Wickramasinghe & Nakamura (2025)
*"A sociohydrological model for evaluating the drought resilience of indigenous and modern dryland irrigation systems in Sri Lanka."* Frontiers in Environmental Science, 13:1535598.

Models farmer cultivation-area decisions as a function of perceived water adequacy (logistic/Verhulst S-curves), comparing the modern New Jaya Ganga (NJG) canal vs. the indigenous, tank-buffered Yoda Ela (YE) canal, both fed by Kalawewa Reservoir, Mahaweli System H (2010–2020). NJG farmers are 18% more dependent on reservoir water and 12% more dependent on rainfall thresholds than YE farmers — small-tank access buffers indigenous farmers from reservoir over-reliance.

Gives an explicit small-tank storage equation `V_T = a_T·R^λ` (λ = 0.38 fitted) and a flexibility/compensation function `F = (V_T/v)(1−r)` linking tank water availability to cultivated area — a candidate seed for an agriculture-response submodule. Command areas: NJG 14,017 ha (46 km canal), YE 4,721 ha (28 km canal). Conveyance efficiencies: 60% (NJG) vs 70% (YE).

### Wickramasinghe & Nakamura (2024)
*"Evaluation of the drought resilience of indigenous irrigation water systems: a case study of dry zone Sri Lanka."* Environmental Research Communications, 6, 035003.

Historical (1985–2021) comparison of the same YE vs. NJG canals using "water duty" (m³ per unit cultivated area) as a drought-reliability metric, with Pettitt change-point tests linking trend breaks to droughts and policy shifts. YE (tank-buffered) is far more drought-resilient: mean water-duty increment in drought years is 16.4% (YE) vs. 58.3% (NJG) — roughly 3.5× less water-stress amplification.

**Relevance (both papers):** Strong empirical justification and calibration targets for the cascade model's drought-buffering behavior, and a real historical water-duty time series (1985–2021, sourced from Mahaweli Authority/WMS records) that could support future calibration. Also references a World Bank/Green Climate Fund cascade-tank rehabilitation program near Madawachchiya, Anuradhapura District, as a pointer to further real-cascade data.

## Socio-economic Context (Agriculture / Population)

### Ratnayake, Kumar, Dharmasena, Kadupitiya, Kariyawasam & Hunter (2021)
*"Sustainability of Village Tank Cascade Systems of Sri Lanka: Exploring Cascade Anatomy and Socio-Ecological Nexus for Ecological Restoration Planning."* Challenges, 12(2), 24.

GIS/spatial and participatory study of the Mahakanumulla Village Tank Cascade System (Nachchaduwa reservoir watershed, Anuradhapura District), mapping cascade "anatomy" (Gasgommana, Kattakaduwa, Perahana land-use zones) for ecological restoration planning. 1,162 village tank cascade systems identified nationally, 90% clustered in North/North-central, North-western, and South/South-eastern zones. Tank storage loss during dry months ≈12% of total storage.

**Relevance:** Cascade structure/typology and regional rainfall/evaporation baselines; qualitative rather than a modeling source.

### Vidanage, Kotagama & Dunusinghe (2022)
*"Sri Lanka's Small Tank Cascade Systems: Building Agricultural Resilience in the Dry Zone."* Ch. 15 in *Climate Change and Community Resilience*, Springer.

Policy/economics review: ~18,000–30,000 small tanks nationally, ~90% in ~1,166 cascades. Village tanks contributed 26% of 2014/15 Maha paddy extent and 25% of 2015 Yala extent. Willingness-to-pay study (Pihimbiyagollawa cascade) values a cascade at LKR 49,328/household/year (~US$264), split across paddy water, other uses, ecology, and biodiversity.

**Relevance:** Economic valuation figures — directly useful for framing the project's ultimate "agricultural economic output" objective and for putting real numbers behind the agriculture→economic-output link in the README's Motivation section.

## Adjacent / Methodological Reference

### Perera, Tamakawa, Rasmy, Ushiyama & Nakamura (2025)
*"Socio-hydrological prediction of soft-path vs. hard-path in flood risk management under climate change: A case study from the Lower Kelani River Basin, Sri Lanka."* Journal of Hydrology: Regional Studies, 58, 102230.

Not about tank irrigation (models flood risk in the Lower Kelani River Basin via HEC-HMS + CMIP5/RCP scenarios + a socio-hydrological ODE system for levee height/population/damage feedback). Kept as a methodological reference for coupling downscaled GCM rainfall/discharge to a socio-economic outcome model, and for its bias-correction pipeline — relevant if the project later wants climate-scenario-driven inflow (Phase 4+ optimization work).

## Video Reference

`Videos on Sri Lanka's Tank Irrigation Systems.docx` — a short curated link list, 6 YouTube URLs. Only one is titled: "Video on Sri Lanka's ancient irrigation systems" (youtube.com/watch?v=YcHhkiIrNqQ). The other five are unannotated and would need spot-checking to assess relevance.

## Storage Note

Full-text PDFs are kept locally at `Desktop/Tank Cascade Sri Lanka India/` and are **intentionally not committed to this public repo** (copyright risk on journal articles, plus binary bloat in git history). This file tracks citations/notes only.
