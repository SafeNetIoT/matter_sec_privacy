import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# === Input Data ===
data = {
    "Meross SP":   ["K1", "K1", "K1", "K1", "K1"],
    "Sailsco SP":  ["K1", "K1", "K1", "K1", "K2"],
    "Tapo SP":     ["K1", "K2", "K3", "K4", "K5"],
    "Meross Hub":  ["K1", "K1", "K1", "K1", "K1"]
}

df = pd.DataFrame(data, index=[1, 2, 3, 4, 5])
df.index.name = "Factory Default"

# === Convert to counts per device per key (for stacking) ===
keys = ["K1", "K2", "K3", "K4", "K5"]
devices = df.columns

counts = pd.DataFrame(0, index=devices, columns=keys)
for device in devices:
    for key in keys:
        counts.loc[device, key] = (df[device] == key).sum()

# === Plot: Stacked Bar Chart ===
plt.figure(figsize=(10, 6))
x = range(len(counts))
bar_width = 0.4  # half the normal width

# color palette (harmonized with academic plotting standards)
colors = {
    "K1": "#4C72B0",  # blue
    "K2": "#55A868",  # green
    "K3": "#C44E52",  # red
    "K4": "#8172B3",  # purple
    "K5": "#CCB974"   # brown/gold
}

bottom_vals = [0] * len(counts)

for key in keys:
    plt.bar(
        x, counts[key],
        bottom=bottom_vals,
        width=bar_width,
        label=key,
        color=colors[key],
        edgecolor="black",
        linewidth=0.5
    )
    bottom_vals = [i + j for i, j in zip(bottom_vals, counts[key])]

# === Labels, axes, legend, and style ===
plt.xticks(x, counts.index, rotation=0, ha="center")
plt.xlabel("Matter Device", fontsize=12)
plt.ylabel("Factory Default (1–5)", fontsize=12)
plt.title("Rotating ID – Change on Factory Reset", fontsize=14, weight="bold")

plt.legend(
    title="Key",
    title_fontsize=11,
    fontsize=10,
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    frameon=False
)

plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
plt.tight_layout()

# === Save and display ===
OUTPUT_FIG = Path("stacked_bar_matter_keys.png")
plt.savefig(OUTPUT_FIG, dpi=300, bbox_inches="tight")
plt.show()

print(f"✅ Stacked bar chart saved as '{OUTPUT_FIG}'")
