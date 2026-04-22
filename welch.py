import matplotlib.pyplot as plt
import statistics
import sys
import os

# Zorg dat de andere bestanden gevonden worden
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation2 import Simulation

# ── Instellingen ──────────────────────────────────────────────────────────────
R_welch  = 20    # aantal replicaties voor Welch
W_welch  = 200   # lange run om transiënte fase te zien
M        = 10    # smoothing venster
SCHEDULE = "schedules/input-S1-14.txt"  # basisconfig
RULE     = 1

# ── Stap 1: draai R replicaties, verzamel movingAvgElectiveAppWT ──────────────
all_series = []

for r in range(R_welch):
    sim = Simulation(SCHEDULE, W_welch, 1, RULE)
    sim.setWeekSchedule()
    sim.resetSystem(r)
    sim.runOneSimulation()
    all_series.append(sim.movingAvgElectiveAppWT[:])
    print(f"Replicatie {r+1}/{R_welch} klaar")

# ── Stap 2: gemiddelde per week over alle replicaties ─────────────────────────
Y = []
for w in range(W_welch):
    week_vals = [all_series[r][w] for r in range(R_welch)
                 if all_series[r][w] > 0]
    Y.append(statistics.mean(week_vals) if week_vals else 0)

# ── Stap 3: smooth met voortschrijdend gemiddelde (venster m) ─────────────────
Y_smooth = []
for w in range(W_welch):
    window = [Y[i] for i in range(max(0, w - M), min(W_welch, w + M + 1))]
    Y_smooth.append(statistics.mean(window))

# ── Stap 4: plot ──────────────────────────────────────────────────────────────
steady_state = statistics.mean(Y_smooth[W_welch // 2:])  # gemiddelde tweede helft

plt.figure(figsize=(13, 5))
plt.plot(range(W_welch), Y,
         color='steelblue', alpha=0.4, linewidth=1, label='Gem. AWT electief per week')
plt.plot(range(W_welch), Y_smooth,
         color='darkgreen', linewidth=2.5, label=f"Smoothed (m={M})")
plt.axhline(steady_state, color='red', linestyle='--', linewidth=1.5,
            label=f'Steady-state niveau ({steady_state:.3f} h)')

plt.xlabel('Week', fontsize=12)
plt.ylabel('Gem. AWT electief (uur)', fontsize=12)
plt.title("Welch's methode — bepaling warm-up periode\n"
          "Baseline: Strategy S1, 14 urgente slots, Rule 1", fontsize=13)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('welch_warmup.png', dpi=150)
plt.show()

print(f"\nSteady-state niveau: {steady_state:.4f} uur")
print("→ Kijk naar de plot: vanaf welke week is de smoothed curve vlak?")
print("  Dat is je warm-up periode L.")