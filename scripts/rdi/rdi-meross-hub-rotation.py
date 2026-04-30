"""
RI-analysis-final.py

Robust script to analyze pcap/pcapng files for Matter mDNS RI= values,
write Excel, and produce a grouped bar chart.

Key differences vs previous versions:
 - We create per-row "kN_key" columns that store the last-4 hex digits of the corresponding RI_N
   (so each trace shows the correct suffix for that trace).
 - kN columns remain numeric counts (one series per kN in the chart).
 - Chart x-axis labels now show only the first 10 characters of the filename (date).
 - Bars are colored consistently by key (last 4 chars), with legend showing the key suffix.
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
    r"D:\Matter\Meross-Hub-UCL",
   
]

OUTPUT_XLSX = "Meross-Hub-UCL.xlsx"
OUTPUT_HIST = "Meross-Hub-UCL.png"

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

    # Sort RIs based on leading numeric two characters if present, else by lexicographic as fallback
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
    """Extract datetime from filenames like 2025-01-21_12.15.48_xxx.pcap"""
    name = Path(filename).stem
    try:
        return datetime.strptime(name[:19], "%Y-%m-%d_%H.%M.%S")
    except Exception:
        return datetime.min

def build_per_row_key_columns(df):
    """
    For each RI_n column, create a per-row column 'k{n}_key' that holds the last 4
    hex characters of the RI value in that row (or '----' if missing).
    """
    ri_columns = sorted([c for c in df.columns if re.match(r"^RI_\d+$", c)],
                        key=lambda x: int(x.split("_")[1]))

    for ri_col in ri_columns:
        n = ri_col.split("_", 1)[1]
        key_col = f"k{n}_key"

        # Build per-row suffix values
        def last4(val):
            if not isinstance(val, str):
                return "----"
            s = val.strip()
            if not s:
                return "----"
            return s[-4:]

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

    # Sort by date extracted from filename
    df["capture_datetime"] = df["pcap_file"].apply(extract_date_from_filename)
    df = df.sort_values(by="capture_datetime").reset_index(drop=True)

    # Find RI and k columns robustly
    ri_columns = sorted([c for c in df.columns if re.match(r"^RI_\d+$", c)],
                        key=lambda x: int(x.split("_")[1]))
    k_columns = sorted([c for c in df.columns if re.match(r"^k\d+$", c)],
                       key=lambda x: int(x[1:]))

    # Add per-row suffix key columns: k1_key, k2_key, ...
    df = build_per_row_key_columns(df)

    # Re-order columns for Excel
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
    ordered_cols = [c for c in ordered_cols if c in df.columns]
    df = df.reindex(columns=ordered_cols, fill_value="")

    # Write Excel
    print(f"\nWriting Excel file to {OUTPUT_XLSX} ...")
    df.to_excel(OUTPUT_XLSX, index=False)

    # === Prepare for plotting ===
    plot_k_cols = [c for c in k_columns if c in df.columns]
    for c in plot_k_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    if plot_k_cols:
        df_plot = df[df[plot_k_cols].sum(axis=1) > 0]
        if not df_plot.empty:
            plt.figure(figsize=(12, 6))
            x = np.arange(len(df_plot))
            total_keys = len(plot_k_cols)
            bar_width = 0.8 / total_keys if total_keys > 0 else 0.8

            # Build consistent key->color mapping across all k columns
            all_keys = []
            for col in plot_k_cols:
                key_col = f"{col}_key"
                if key_col in df_plot.columns:
                    all_keys.extend(df_plot[key_col].tolist())
            unique_keys = sorted(set(k for k in all_keys if k not in ("", "----")))
            key_color_map = {k: cm.get_cmap("tab20")(i % 20) for i, k in enumerate(unique_keys)}

            # Plot each k column
            for idx, col in enumerate(plot_k_cols):
                key_col = f"{col}_key"
                colors = [key_color_map.get(k, "gray") for k in df_plot[key_col]]
                plt.bar(x + idx * bar_width,
                        df_plot[col].astype(float).tolist(),
                        width=bar_width,
                        color=colors,
                        label=f"{key_col[-4:]}" if idx==0 else "")  # dummy label, legend handled below

            # X-axis labels
            x_labels = [Path(row["pcap_file"]).stem[:10] for _, row in df_plot.iterrows()]
            plt.xticks(x + bar_width * (total_keys / 2 - 0.5),
                       x_labels, rotation=45, ha="right", fontsize=12, fontweight="bold")

            # Y-axis and X-axis labels
            plt.ylabel("RI Packet Count", fontsize=14, fontweight="bold")
            plt.xlabel("Capture Date", fontsize=14, fontweight="bold")

            # Title
            source_dir = Path(PCAP_DIRS[0]).name
            plt.title(f"RI= Key usage - Device = {source_dir}", fontsize=18, fontweight="bold")

            # Legend: show all unique keys with their colors
            from matplotlib.patches import Patch
            legend_handles = [Patch(color=key_color_map[k], label=k) for k in unique_keys]
            plt.legend(handles=legend_handles, title="Key (last 4 chars)", fontsize=12)
            plt.tight_layout()
            plt.savefig(OUTPUT_HIST)
            print(f"Grouped histogram saved to {OUTPUT_HIST}")
        else:
            print("No data for histogram.")
    else:
        print("No k-columns — skipping histogram.")

    # Print short summary
    all_unique_ris = set()
    for c in ri_columns:
        all_unique_ris.update(v for v in df[c] if isinstance(v, str) and v.strip())
    print(f"\n✅ Total unique RI values found across all traces: {len(all_unique_ris)}")
    print("Done.")

if __name__ == "__main__":
    main()
