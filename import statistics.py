import statistics
import math
from scipy.stats import t

# Plak hier je 30 OV-waarden uit de Excel (kolom OV, sheet Replications)
results = [...]

n0 = len(results)
x_bar = statistics.mean(results)
S = statistics.stdev(results)

# 95% betrouwbaarheidsinterval
t_val = t.ppf(0.975, df=n0 - 1)
half_width = t_val * S / math.sqrt(n0)
print(f"Gemiddelde OV:  {x_bar:.4f}")
print(f"Standaarddev:   {S:.4f}")
print(f"95% CI:         [{x_bar - half_width:.4f}, {x_bar + half_width:.4f}]")
print(f"Half-width:     {half_width:.4f}")

# Vereist aantal replicaties (5% precisie)
epsilon = 0.05 * x_bar
n = n0
for _ in range(50):
    t_val = t.ppf(0.975, df=n - 1)
    n_new = math.ceil((t_val * S / epsilon) ** 2)
    if n_new == n:
        break
    n = n_new
print(f"Vereist R:      {n}")