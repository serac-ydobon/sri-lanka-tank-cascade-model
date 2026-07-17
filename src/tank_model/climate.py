"""Stochastic rainfall generator: seasonal Markov chain (wet/dry occurrence)
+ Gamma distribution (rainfall amount on wet days).

Calibrated per calendar month to capture the Maha/Yala bimodal monsoon
seasonality. Purpose: generate many cheap synthetic daily rainfall
realizations -- as opposed to running an expensive GCM/RCM physical
climate simulation per scenario -- to drive Monte Carlo climate-scenario
ensembles through the cascade model, feeding the project's eventual
optimization layer (see README Roadmap, Phase 4+).

Method follows the classic Richardson (1981)-style stochastic weather
generator (WGEN): a first-order two-state Markov chain for wet/dry
occurrence, with a Gamma distribution for the rainfall amount on wet
days, both re-fit for each calendar month. This is the same style of
model published for Sri Lankan dry-zone stations (see
docs/literature_notes.md) -- non-stationary Markov chain + Gamma
amounts, shown to fit dry-zone stations (e.g. Anuradhapura) better than
wet-zone stations.
"""

import datetime as dt

import numpy as np


def _wet_mask(rainfall, wet_threshold):
    return np.asarray(rainfall) > wet_threshold


def fit_monthly_markov_gamma(months, rainfall, wet_threshold=0.1, eps=1e-6):
    """Fit a first-order Markov chain (wet/dry) and Gamma amount distribution
    per calendar month from an observed daily rainfall record.

    Parameters
    ----------
    months : array-like of int, shape (n,)
        Calendar month (1-12) for each day, same length/order as `rainfall`.
    rainfall : array-like of float, shape (n,)
        Daily rainfall depth (mm), in chronological order.
    wet_threshold : float
        Rainfall (mm) above which a day counts as "wet". 0.1mm is the
        conventional trace threshold used in the cited Sri Lanka studies.
    eps : float
        Small floor to avoid zero/degenerate probabilities or Gamma
        parameters for months with very few wet days.

    Returns
    -------
    dict : {month (1-12): {"p_wet_given_dry": float, "p_wet_given_wet": float,
                            "gamma_shape": float, "gamma_scale": float}}

    Notes
    -----
    Transitions are read off consecutive entries in `rainfall` (index i
    vs. i-1). If the record has date gaps, transitions spanning a gap
    should be dropped by the caller before fitting -- not detected here.
    """
    months = np.asarray(months, dtype=int)
    rainfall = np.asarray(rainfall, dtype=float)
    wet = _wet_mask(rainfall, wet_threshold)

    params = {}
    for m in range(1, 13):
        idx_month = np.where(months == m)[0]
        idx_month = idx_month[idx_month > 0]  # need a previous day to know the transition

        n_dry_to_wet = 0
        n_dry_total = 0
        n_wet_to_wet = 0
        n_wet_total = 0
        for i in idx_month:
            prev_wet = wet[i - 1]
            curr_wet = wet[i]
            if prev_wet:
                n_wet_total += 1
                n_wet_to_wet += int(curr_wet)
            else:
                n_dry_total += 1
                n_dry_to_wet += int(curr_wet)

        p_wet_given_dry = (n_dry_to_wet / n_dry_total) if n_dry_total > 0 else eps
        p_wet_given_wet = (n_wet_to_wet / n_wet_total) if n_wet_total > 0 else eps
        p_wet_given_dry = min(max(p_wet_given_dry, eps), 1 - eps)
        p_wet_given_wet = min(max(p_wet_given_wet, eps), 1 - eps)

        amounts = rainfall[(months == m) & wet]
        if amounts.size >= 2 and amounts.mean() > 0:
            mean = amounts.mean()
            var = amounts.var(ddof=1)
            if var <= 0:
                var = eps
            # method-of-moments Gamma fit: shape=mean^2/var, scale=var/mean
            gamma_shape = max(mean ** 2 / var, eps)
            gamma_scale = max(var / mean, eps)
        else:
            # not enough wet days this month to fit -- nominal fallback
            # so simulation doesn't crash; flagged, not silently "correct"
            gamma_shape = eps
            gamma_scale = amounts.mean() if amounts.size > 0 else eps

        params[m] = {
            "p_wet_given_dry": p_wet_given_dry,
            "p_wet_given_wet": p_wet_given_wet,
            "gamma_shape": gamma_shape,
            "gamma_scale": gamma_scale,
        }
    return params


def simulate_rainfall(n_days, start_date, params, wet_threshold=0.1, start_wet=False, rng=None):
    """Generate a synthetic daily rainfall series using calibrated
    monthly Markov+Gamma parameters.

    Parameters
    ----------
    n_days : int
        Number of days to simulate.
    start_date : datetime.date
        Calendar date of the first simulated day (real calendar dates are
        used so month lengths and leap years are handled correctly).
    params : dict
        Output of `fit_monthly_markov_gamma`.
    start_wet : bool
        Wet/dry state assumed for the (unobserved) day before simulation
        starts -- only affects the first day's transition probability.
    rng : numpy.random.Generator, optional
        Random generator; a new default one is created if not given
        (pass one in explicitly for reproducible runs).

    Returns
    -------
    dates : list[datetime.date], length n_days
    rainfall : numpy.ndarray, shape (n_days,)
    """
    if rng is None:
        rng = np.random.default_rng()

    dates = [start_date + dt.timedelta(days=i) for i in range(n_days)]
    rainfall = np.zeros(n_days)
    prev_wet = start_wet

    for t, d in enumerate(dates):
        p = params[d.month]
        p_wet = p["p_wet_given_wet"] if prev_wet else p["p_wet_given_dry"]
        is_wet = rng.random() < p_wet

        if is_wet:
            amount = rng.gamma(p["gamma_shape"], p["gamma_scale"])
            rainfall[t] = max(amount, wet_threshold)
        else:
            rainfall[t] = 0.0

        prev_wet = is_wet

    return dates, rainfall
