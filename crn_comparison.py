import statistics
import math
from scipy.stats import t
from openpyxl import load_workbook
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from simulation2 import Simulation

# ── Instellingen ──────────────────────────────────────────────────────────────
R        = 30
W        = 20
SCHEDULE = "schedules/input-S1-14.txt"
RULE     = 1

# ── Met CRN (aparte random.Random streams per replicatie) ─────────────────────
print("Draaien MET CRN...")
results_crn = []
sim_crn = Simulation(SCHEDULE, W, R, RULE)
sim_crn.setWeekSchedule()
for r in range(R):
    sim_crn.resetSystem(r)
    sim_crn.runOneSimulation()
    ov = sim_crn.avgElectiveAppWT * sim_crn.weightEl + sim_crn.avgUrgentScanWt * sim_crn.weightUr
    results_crn.append(ov)
    print(f"  rep {r+1:2d}: OV = {ov:.4f}")

# ── Zonder CRN (globale random seed, geen aparte streams) ────────────────────
print("\nDraaien ZONDER CRN...")
import random

results_nocrn = []
sim_nocrn = Simulation(SCHEDULE, W, R, RULE)
sim_nocrn.setWeekSchedule()
for r in range(R):
    # Reset alles manueel maar gebruik één globale seed
    sim_nocrn.patients = []
    sim_nocrn.avgElectiveAppWT = 0.0
    sim_nocrn.avgElectiveScanWT = 0.0
    sim_nocrn.avgUrgentScanWt = 0.0
    sim_nocrn.avgOT = 0.0
    sim_nocrn.movingAvgElectiveAppWT = [0.0] * W
    sim_nocrn.movingAvgElectiveScanWT = [0.0] * W
    sim_nocrn.movingAvgUrgentScanWT = [0.0] * W
    sim_nocrn.movingAvgOT = [0.0] * W

    # Één gedeelde RNG voor alle streams → geen CRN
    shared_rng = random.Random(r * 999)
    sim_nocrn.rng_el_arrival  = shared_rng
    sim_nocrn.rng_ur_arrival  = shared_rng
    sim_nocrn.rng_tardiness   = shared_rng
    sim_nocrn.rng_noshow      = shared_rng
    sim_nocrn.rng_el_duration = shared_rng
    sim_nocrn.rng_scan_type   = shared_rng
    sim_nocrn.rng_ur_duration = shared_rng

    sim_nocrn.runOneSimulation()
    ov = sim_nocrn.avgElectiveAppWT * sim_nocrn.weightEl + sim_nocrn.avgUrgentScanWt * sim_nocrn.weightUr
    results_nocrn.append(ov)
    print(f"  rep {r+1:2d}: OV = {ov:.4f}")

# ── Vergelijking ──────────────────────────────────────────────────────────────
mean_crn   = statistics.mean(results_crn)
stdev_crn  = statistics.stdev(results_crn)
var_crn    = statistics.variance(results_crn)

mean_nocrn  = statistics.mean(results_nocrn)
stdev_nocrn = statistics.stdev(results_nocrn)
var_nocrn   = statistics.variance(results_nocrn)

reductie = (1 - var_crn / var_nocrn) * 100

t_val = t.ppf(0.975, df=R - 1)
hw_crn   = t_val * stdev_crn  / math.sqrt(R)
hw_nocrn = t_val * stdev_nocrn / math.sqrt(R)

print("\n" + "="*55)
print(f"{'':20s} {'Met CRN':>15s} {'Zonder CRN':>15s}")
print("="*55)
print(f"{'Gemiddelde OV':20s} {mean_crn:>15.4f} {mean_nocrn:>15.4f}")
print(f"{'Standaarddev':20s} {stdev_crn:>15.4f} {stdev_nocrn:>15.4f}")
print(f"{'Variantie':20s} {var_crn:>15.6f} {var_nocrn:>15.6f}")
print(f"{'95% CI half-width':20s} {hw_crn:>15.4f} {hw_nocrn:>15.4f}")
print("="*55)
print(f"\nVariantiereductie door CRN: {reductie:.1f}%")
print(f"CI is {hw_nocrn/hw_crn:.1f}x breder zonder CRN")
