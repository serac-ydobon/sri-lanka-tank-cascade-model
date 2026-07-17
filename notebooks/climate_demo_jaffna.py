import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# make src/ importable without a package install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from tank_model.climate import fit_monthly_markov_gamma, simulate_rainfall
from tank_model.data_io import load_daily_rainfall_jaffna


def main():
    daily = load_daily_rainfall_jaffna(station="JAFFNA")
    print(f"Observed record: {len(daily)} days, {daily['date'].min().date()} to {daily['date'].max().date()}")

    months = daily["date"].dt.month.to_numpy()
    rainfall = daily["P"].to_numpy(dtype=float)

    params = fit_monthly_markov_gamma(months, rainfall)

    print("\nCalibrated monthly parameters:")
    for m in range(1, 13):
        p = params[m]
        print(f"  Month {m:2d}: P(wet|dry)={p['p_wet_given_dry']:.3f}  "
              f"P(wet|wet)={p['p_wet_given_wet']:.3f}  "
              f"Gamma(shape={p['gamma_shape']:.3f}, scale={p['gamma_scale']:.3f})")

    # Generate one synthetic realization of the same length as the observed record
    rng = np.random.default_rng(42)
    n_days = len(daily)
    start_date = daily["date"].iloc[0].date()
    sim_dates, sim_rainfall = simulate_rainfall(n_days, start_date, params, rng=rng)

    # ================= Sanity check: observed vs. synthetic =================
    years = n_days / 365.25
    obs_annual_mean = rainfall.sum() / years
    sim_annual_mean = sim_rainfall.sum() / years
    obs_wet_frac = (rainfall > 0.1).mean()
    sim_wet_frac = (sim_rainfall > 0.1).mean()

    print("\nObserved vs. synthetic (sanity check -- should be broadly similar,")
    print("not identical, since this is a stochastic realization):")
    print(f"  Mean annual rainfall: observed={obs_annual_mean:.1f} mm/yr, synthetic={sim_annual_mean:.1f} mm/yr")
    print(f"  Wet-day fraction:     observed={obs_wet_frac:.3f}, synthetic={sim_wet_frac:.3f}")

    # Monthly-average comparison (mm per ~30-day month, for a quick visual check)
    obs_monthly = pd.Series(rainfall).groupby(months).mean() * 30
    sim_months = np.array([d.month for d in sim_dates])
    sim_monthly = pd.Series(sim_rainfall).groupby(sim_months).mean() * 30

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(1, 13)
    width = 0.35
    ax.bar(x - width / 2, obs_monthly.reindex(x, fill_value=0), width, label="Observed")
    ax.bar(x + width / 2, sim_monthly.reindex(x, fill_value=0), width, label="Synthetic")
    ax.set_xticks(x)
    ax.set_xlabel("Month")
    ax.set_ylabel("Avg. monthly rainfall (mm, ~30-day)")
    ax.set_title("Jaffna: Observed vs. Markov+Gamma Synthetic Rainfall")
    ax.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
