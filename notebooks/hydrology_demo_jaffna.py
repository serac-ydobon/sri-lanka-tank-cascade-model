import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Slider

# make src/ importable without a package install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from tank_model.hydrology import toymodel_new_4
from tank_model.data_io import load_daily_rainfall_jaffna


def main():
    start_year = 2022
    end_year = 2024

    daily = load_daily_rainfall_jaffna(station="JAFFNA")
    daily = daily[(daily["date"].dt.year >= start_year) & (daily["date"].dt.year <= end_year)].reset_index(drop=True)

    print("Days:", len(daily), "from", daily["date"].min().date(), "to", daily["date"].max().date())

    P = daily["P"].to_numpy(dtype=float)

    Ep_const = 5.0  # <--
    Ep = np.full_like(P, Ep_const, dtype=float)

    DATA = np.column_stack([np.zeros_like(P), P, Ep])

    # Parameters: [mir, Su_max, Ts, Tf, beta]
    PAR = np.array([175.0, 90.0, 100.0, 1.0, 1.0], dtype=float)

    Ea, QF, R, QS, QT, Sf, Su, Ss, St, AL, IE, SE, Pump = toymodel_new_4(DATA, PAR)

    # ================= Water balance check =================
    S0 = 0.2
    Su0 = S0
    Sf0 = S0
    Ss0 = S0

    dSu = np.empty_like(Su)
    dSf = np.empty_like(Sf)
    dSs = np.empty_like(Ss)

    dSu[0] = Su[0] - Su0
    dSf[0] = Sf[0] - Sf0
    dSs[0] = Ss[0] - Ss0

    dSu[1:] = Su[1:] - Su[:-1]
    dSf[1:] = Sf[1:] - Sf[:-1]
    dSs[1:] = Ss[1:] - Ss[:-1]

    dS_total = dSu + dSf + dSs

    residual_naive = P - (Ea + QF + QS)  # the change of storage without pumping

    residual_full = P - (Ea + QF + QS + dS_total + Pump)

    print("\nFull balance check: P ?= E + QF + QS + dS_total")
    print("Max abs residual:", np.max(np.abs(residual_full)))
    print("Mean abs residual:", np.mean(np.abs(residual_full)))

    # Cumulative check
    cum_P = np.sum(P)
    cum_E = np.sum(Ea)
    cum_QF = np.sum(QF)
    cum_QS = np.sum(QS)
    delta_storage_total = (Su[-1] - Su0) + (Sf[-1] - Sf0) + (Ss[-1] - Ss0)
    cum_Pump = np.sum(Pump)

    print("\nCumulative totals:")
    print(f"Sum(P)   = {cum_P:.6f}")
    print(f"Sum(E)   = {cum_E:.6f}")
    print(f"Sum(QF)  = {cum_QF:.6f}")
    print(f"Sum(QS)  = {cum_QS:.6f}")
    print(f"Delta S  = {delta_storage_total:.6f}")
    print(f"Sum(E+QF+QS)              = {(cum_E + cum_QF + cum_QS):.6f}")
    print(f"Sum(Pump)= {cum_Pump:.6f}")
    print(f"Sum(E+QF+QS+Pump)+DeltaS = {(cum_E + cum_QF + cum_QS + cum_Pump + delta_storage_total):.6f}")
    print(f"Cumulative residual full = {(cum_P - (cum_E + cum_QF + cum_QS + cum_Pump + delta_storage_total)):.6f}")

    # Optional: make a dataframe for inspection
    wb = pd.DataFrame({
        "date": daily["date"],
        "P": P,
        "E": Ea,
        "QF": QF,
        "QS": QS,
        "dSu": dSu,
        "dSf": dSf,
        "dSs": dSs,
        "dS_total": dS_total,
        "residual_naive": residual_naive,
        "residual_full": residual_full,
        "Pumping": Pump
    })

    print("\nLargest naive residual days:")
    print(wb.loc[wb["residual_full"].abs().nlargest(10).index,
                 ["date", "P", "E", "QF", "QS", "dS_total", "residual_naive", "residual_full"]])

    # ---------------- following are ugly graphs, BUT GOOD USAGE FOR OVERVIEW IF CHOOSING A SHORT LENGTHS OF TIME --------------
    # print(Ea + QF + Qs == Sf + Ss + )

    # t = daily["date"]

    # fig, axes = plt.subplots(7, 1, sharex=True, figsize=(12, 14))

    # axes[0].plot(t, Su); axes[0].set_ylabel("S_u (mm)")
    # axes[1].plot(t, Sf); axes[1].set_ylabel("S_F (mm)")
    # axes[2].plot(t, Ss); axes[2].set_ylabel("S_s (mm)")

    # axes[3].plot(t, QS); axes[3].set_ylabel("Q_s (mm/day)")
    # axes[4].plot(t, QF); axes[4].set_ylabel("Q_F (mm/day)")

    # axes[5].plot(t, R);  axes[5].set_ylabel("R (mm/day)")
    # axes[6].plot(t, Ea); axes[6].set_ylabel("E (mm/day)")
    # axes[6].set_xlabel("Date")

    # axes[6].xaxis.set_major_locator(mdates.MonthLocator())
    # axes[6].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    # fig.autofmt_xdate()

    # fig.suptitle("JAFFNA 2024: States & Fluxes", y=0.995)
    # plt.tight_layout()
    # plt.show()
    # --------------------------------------------------------------------------------------------------

    t = daily["date"]

    series = [
        ("S_u (mm)", Su),
        ("S_F (mm)", Sf),
        ("S_s (mm)", Ss),
        ("Q_s (mm/day)", QS),
        ("Q_F (mm/day)", QF),
        ("R (mm/day)", R),
        ("E (mm/day)", Ea),
    ]

    fig, ax = plt.subplots(figsize=(17, 10))
    plt.subplots_adjust(bottom=0.18)

    idx0 = 0
    (line,) = ax.plot(t, series[idx0][1])
    ax.set_title(series[idx0][0])
    ax.set_xlabel("Date")
    ax.set_ylabel(series[idx0][0])

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()

    # Slider
    slider_ax = fig.add_axes([0.15, 0.06, 0.7, 0.04])
    sld = Slider(slider_ax, "Plot", 0, len(series) - 1, valinit=idx0, valstep=1)

    def update(i):
        i = int(i)
        ylab, y = series[i]
        line.set_ydata(y)
        ax.relim()
        ax.autoscale_view()
        ax.set_title(ylab)
        ax.set_ylabel(ylab)
        fig.canvas.draw_idle()

    sld.on_changed(update)

    def on_key(event):
        if event.key in ["right", "down", "pagedown"]:
            sld.set_val(min(int(sld.val) + 1, len(series) - 1))
        elif event.key in ["left", "up", "pageup"]:
            sld.set_val(max(int(sld.val) - 1, 0))

    fig.canvas.mpl_connect("key_press_event", on_key)

    fig.suptitle(f"JAFFNA {start_year}-{end_year}: States & Fluxes", y=0.995)
    plt.show()


if __name__ == "__main__":
    main()
