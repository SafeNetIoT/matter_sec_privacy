import matplotlib.pyplot as plt
import pandas as pd

# === Input Data ===
# Columns correspond to Matter devices, rows to factory defaults (1–5)
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

# Count occurrences of each key for each device
counts = pd.DataFrame(0, index=devices, columns=keys)
for device in devices:
    for key in keys:
        counts.loc[device, key] = (df[device] == key).sum()

# === Plot: Stacked Bar Chart ===
plt.figure(figsize=(10, 6))

bottom_vals = [0] * len(counts)
colors = {
    "K1": "#4C72B0",
    "K2": "#55A868",
    "K3": "#C44E52",
    "K4": "#8172B3",
    "K5": "#CCB974"
}

for key in keys:
    plt.bar(counts.index, counts[key], bottom=bottom_vals,
            label=key, color=colors.get(key, None))
    bottom_vals = [i + j for i, j in zip(bottom_vals, counts[key])]

# === Labels, title, legend ===
plt.xlabel("Matter Device")
plt.ylabel("Factory Default (1–5)")
plt.title("Rotating ID – Change on Factory Reset")
plt.legend(title="Key", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

# === Save / show ===
plt.savefig("stacked_bar_matter_keys.png", dpi=300)
plt.show()
print("✅ Stacked bar chart saved as 'stacked_bar_matter_keys.png'")
