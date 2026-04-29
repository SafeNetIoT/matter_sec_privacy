"""
RI-analysis-final.py (Updated)

- No title
- No X-axis label
- Legend uses k1, k2, k3... (NOT last 4 chars)
- High-contrast tab10 colors (no similar blues)
- Larger font sizes for axis labels
"""

import re
import subprocess
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from datetime import datetime

# === CONFIGURATION ===
PCAP_DIRS = [
    r"D:\Northeastern-Matter-Data\Cync-Matter-Plug-1",
]

OUTPUT_XLSX = "Cync-Matter-Plug-new2.xlsx"
OUTPUT_HIST = "Cync-Matter-Plug-new2.png"

# Regex to extract RI hex strings
RI_RE = re.compile(r"RI=([0-9A-Fa-f]+)")

# tshark command template
TSHARK_CMD_TEMPLATE = [
    "tshark",
    "-r", "{pcap}",
    "-Y", "udp.port == 5353 && dns.txt",
    "-T", "fields",
    "-e", "frame.time_epoch",
    "-e", "dns.txt"
]

def run_tshark_on_pcap(pcap_path):
    cmd = [part.format(pcap=pcap_path) for part in TSHARK_CMD_TEMPLATE]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        raise RuntimeError("tshark not found. Install Wireshark/tshark and add to PATH.")

    out = proc.stdout.decode(errors="ignore")
    lines = []
    for raw in out.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            continue
        epoch = parts[0].strip()
        txt = "\t".join(parts[1:]).strip()
        lines.append((epoch, txt))
    return lines

def analyze_pcap_file(pcap_path):
    extracted = run_tshark_on_pcap(pcap_path)

    ri_counts = {}
    packet_count = 0

    for _, txt in extracted:
        matches = RI_RE.findall(txt)
        if not matches:
            continue
        packet_count += 1
        for m in matches:
            ri_counts[m] = ri_counts.get(m, 0) + 1

    if not ri_counts:
        return None

    def ri_sort_key(v):
        if len(v) >= 2 and v[:2].isdigit():
            return (0, int(v[:2]), v)
        return (1, v)

    unique_ri_values = sorted(ri_counts.keys(), key=ri_sort_key)

    print(f"Analyzing {Path(pcap_path).name} ... found {len(unique_ri_values)} RI values")

    result = {
        "pcap_file": pcap_path,
        "unique_RI_count": len(unique_ri_values)
    }

    # Create RI_1, RI_2, ... and k1, k2, ...
    for i, ri in enumerate(unique_ri_values, start=1):
        result[f"RI_{i}"] = ri
        result[f"k{i}"] = ri_counts[ri]

    result["RI_packet_count"] = packet_count
    return result

def find_pcaps(dirs):
    pcaps = []
    for d in dirs:
        path = Path(d)
        if not path.exists():
            print(f"Warning: {d} not found, skipping.")
            continue
        for f in path.iterdir():
            if f.is_file() and f.suffix.lower() in (".pcap", ".pcapng"):
                pcaps.append(str(f))
    return sorted(pcaps)

def extract_date_from_filename(filename):
    name = Path(filename).stem
    try:
        return datetime.strptime(name[:19], "%Y-%m-%d_%H.%M.%S")
    except Exception:
        return datetime.min

def build_per_row_key_columns(df):
    """Generate _key columns (last 4 chars) for Excel, not used in chart."""
    ri_columns = sorted(
        [c for c in df.columns if re.match(r"^RI_\d+$", c)],
        key=lambda x: int(x.split("_")[1])
    )

    for ri_col in ri_columns:
        n = ri_col.split("_", 1)[1]
        key_col = f"k{n}_key"

        def last4(val):
            if not isinstance(val, str) or not val.strip():
                return "----"
            return val.strip()[-4:]

        df[key_col] = df[ri_col].apply(last4)

    return df

def main():
    pcaps = find_pcaps(PCAP_DIRS)
    if not pcaps:
        print("No pcap or pcapng files found.")
        return

    results = []
    for p in pcaps:
        try:
            res = analyze_pcap_file(p)
            if res:
                results.append(res)
        except Exception as e:
            print(f"Error analyzing {p}: {e}")

    if not results:
        print("No traces with RI data found — nothing to chart or export.")
        return

    df = pd.DataFrame(results)
    df["capture_datetime"] = df["pcap_file"].apply(extract_date_from_filename)
    df = df.sort_values(by="capture_datetime").reset_index(drop=True)

    # Identify RI and k columns
    ri_columns = sorted([c for c in df.columns if re.match(r"^RI_\d+$", c)],
                        key=lambda x: int(x.split("_")[1]))
    k_columns = sorted([c for c in df.columns if re.match(r"^k\d+$", c)],
                       key=lambda x: int(x[1:]))

    df = build_per_row_key_columns(df)

    # Reorder for Excel
    ordered_cols = ["pcap_file", "unique_RI_count"]
    for i, ri_col in enumerate(ri_columns, start=1):
        ordered_cols.append(ri_col)
        kcol = f"k{i}"
        if kcol in df.columns:
            ordered_cols.append(kcol)
        keycol = f"k{i}_key"
        if keycol in df.columns:
            ordered_cols.append(keycol)
    if "RI_packet_count" in df.columns:
        ordered_cols.append("RI_packet_count")

    df = df.reindex(columns=ordered_cols, fill_value="")

    print(f"\nWriting Excel file to {OUTPUT_XLSX} ...")
    df.to_excel(OUTPUT_XLSX, index=False)

    # === Plotting ===
    plot_k_cols = [c for c in k_columns if c in df.columns]
    for c in plot_k_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    if plot_k_cols:
        df_plot = df[df[plot_k_cols].sum(axis=1) > 0]
        if not df_plot.empty:

            plt.figure(figsize=(12, 6))
            x = np.arange(len(df_plot))
            total_keys = len(plot_k_cols)
            bar_width = 0.8 / total_keys

            # High-contrast color map
            cmap = cm.get_cmap("tab10")

            # Plot each k column with clear unique color
            for idx, col in enumerate(plot_k_cols):
                series_color = cmap(idx % 10)
                plt.bar(
                    x + idx * bar_width,
                    df_plot[col].astype(float).tolist(),
                    width=bar_width,
                    color=series_color,
                    label=col  # legend shows k1, k2, k3...
                )

            # X-axis
            x_labels = [Path(row["pcap_file"]).stem[:10] for _, row in df_plot.iterrows()]
            plt.xticks(
                x + bar_width * (total_keys / 2 - 0.5),
                x_labels,
                rotation=45,
                ha="right",
                fontsize=20,
                fontweight="bold"
            )

            # Y-axis
            plt.ylabel("RI Packet Count", fontsize=20, fontweight="bold")

            # No title, no X label
            # plt.xlabel(...)
            # plt.title(...)

            # Legend
            plt.legend(title="Key", fontsize=16)

            plt.tight_layout()
            plt.savefig(OUTPUT_HIST)
            print(f"Grouped histogram saved to {OUTPUT_HIST}")
        else:
            print("No data for histogram.")
    else:
        print("No k-columns — skipping histogram.")

    # Summary
    all_unique_ris = set()
    for c in ri_columns:
        all_unique_ris.update(v for v in df[c] if isinstance(v, str) and v.strip())
    print(f"\n✅ Total unique RI values found across all traces: {len(all_unique_ris)}")
    print("Done.")

if __name__ == "__main__":
    main()
