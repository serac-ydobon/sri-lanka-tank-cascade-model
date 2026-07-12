"""Catchment rainfall-runoff generation (three-store conceptual model).

Ported verbatim from the original standalone script (Desktop/Hydrological
Model/Hydrology Model.py) -- function bodies below are an exact copy, not
a rewrite. Output units are mm per timestep (depth); convert to volume
(x catchment area) before using as a tank's Inflow_t.
"""

import numpy as np

#fast-response surface flow reservoir
def SF_eq(S0, P, alpha, Tf, SE):
    ie = P * alpha
    S_dt = S0 + (P * alpha) + SE - (S0 / Tf)
    Qf = S0 / Tf
    return Qf, S_dt, ie

# unsaturated zone reservoir
def SU_eq(Su_0, P, Ep, Sumax, alpha, beta):
    Su_0 = Su_0 + (P * (1.0 - alpha))

    if Su_0 < Sumax:
        R = 0.0
    else:
        R = Su_0 - Sumax

    Su_0 = Su_0 - R

    # evaporation
    E = Ep * (Su_0 / Sumax) if Sumax != 0 else 0.0
    if E > Ep:
        E = Ep
    Su_0 = Su_0 - E

    S_dt = Su_0
    r = R * beta
    se = R * (1.0 - beta)
    return r, se, E, S_dt

# slow-response saturated zone reservoir
#  ADD PUMPING later --> added
def SS_eq(S0, R, Ts, pump_demand):
    Qs = S0 / Ts

    available_for_pumping = S0 + R - Qs
    if available_for_pumping < 0:
        available_for_pumping = 0.0

    pumping_actual = min(pump_demand, available_for_pumping) # pump as much as it can

    S_dt = S0 + R - Qs - pumping_actual
    return Qs, pumping_actual, S_dt


def toymodel_new_4(data, par, eps=1e-12):
    data = np.asarray(data, dtype=float)
    par = np.asarray(par, dtype=float)

    M = data.shape[0]
    P = data[:, 1]
    Ep = data[:, 2]

    mir = par[0]
    Su_max = par[1]
    Ts = par[2]
    Tf = par[3]
    beta = par[4]

    # Initialization (all column vectors in MATLAB -> 1D arrays here)
    QF = np.zeros(M)
    QS = np.zeros(M)
    QT = np.zeros(M)
    R = np.zeros(M)
    Sf = np.zeros(M)
    Su = np.zeros(M)
    Ss = np.zeros(M)
    Ea = np.zeros(M)
    AL = np.zeros(M)
    IE = np.zeros(M)
    SE = np.zeros(M)
    Pump = np.zeros(M)

    # Initial values
    S0 = 0.2
    Su_dt = S0
    Ss_dt = S0
    Sf_dt = S0

    # MAIN FLOW ROUTINE (loop 1)
    for t in range(M):
        if P[t] > 0:
            # mir_actual = mir*(Su_max/Su_dt);
            mir_actual = mir * (Su_max / max(Su_dt, eps))

            x = P[t] / mir_actual
            # AL(t) = 1 - (1 - exp(-P/mir_actual) )/(P/mir_actual); THIS IS THE ALPHA_t
            AL[t] = 1.0 - (1.0 - np.exp(-x)) / x
        else:
            AL[t] = 0.0

        # Unsaturated zone water balance
        r, se, E, Su_dt = SU_eq(Su_dt, P[t], Ep[t], Su_max, AL[t], beta)

        R[t] = r
        Ea[t] = E
        Su[t] = Su_dt
        SE[t] = se

        # Saturated zone
        Sb = 30.0
        if t == 0:
            pump_demand = 1.5 * S0 / Sb
        else:
            pump_demand = 1.5 * Ss[t-1] / Sb

        Qs, pumping, Ss_dt = SS_eq(Ss_dt, r, Ts, pump_demand)

        QS[t] = Qs
        Ss[t] = Ss_dt
        Pump[t] = pumping
    # Fastflow (loop 2)
    for t in range(M):
        Qf, Sf_dt, ie = SF_eq(Sf_dt, P[t], AL[t], Tf, SE[t])
        QF[t] = Qf
        Sf[t] = Sf_dt
        IE[t] = ie

    QT = QF + QS
    St = Su + Ss + Sf  # Total storage should be the storage in all the system

    return Ea, QF, R, QS, QT, Sf, Su, Ss, St, AL, IE, SE, Pump
