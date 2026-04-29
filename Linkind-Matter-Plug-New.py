"""
RI-analysis-final.py — GLOBAL RI indexing + stacked plotting

- No title for Excel
- Legend uses k1, k2, k3...
- Stacked bar chart (NOT grouped)
- Bars centered and wide (matches desired format)
- High-contrast tab10 colors
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
    r"D:\Northeastern-Matter-Data\Linkind-Matter-Plug",
]

OUTPUT_XLSX = "Linkind-Matter-Plug-new.xlsx"
OUTPUT_HIST = "Linkind-Matter-Plug-new.png"

# Regex to extract RI hex strings (4–64 chars)
RI_RE = re.compile(r"RI=([0-9A-Fa-f]{4,64})")

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
    """Run tshark and return (epoch, txt) tuples per line."""
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


def extract_ri_values_from_pcap(pcap_path):
    """Extract RI counts from a pcap file."""
    extracted = run_tshark_on_pcap(pcap_path)

    ri_counts = {}
    packet_count = 0

    for _, txt in extracted:
        matches = RI_RE.findall(txt)
        if not matches:
            continue
        packet_count += 1
        for ri in matches:
            ri_counts[ri] = ri_counts.get(ri, 0) + 1

    return ri_counts, packet_count


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


def main():
    pcaps = find_pcaps(PCAP_DIRS)
    if not pcaps:
        print("No pcap or pcapng files found.")
        return

    per_file_data = []
    all_ris = set()

    # === First pass: collect ALL unique RIs globally ===
    for p in pcaps:
        ri_counts, packet_count = extract_ri_values_from_pcap(p)

        for ri in ri_counts:
            all_ris.add(ri)

        per_file_data.append({
            "pcap_file": p,
            "ri_counts": ri_counts,
            "packet_count": packet_count
        })

    if not all_ris:
        print("No RI values found in any pcap.")
        return

    # Sort global RI list (00, 01, …, non-numeric)
    def ri_sort_key(v):
        if len(v) >= 2 and v[:2].isdigit():
            return (0, int(v[:2]), v)
        return (1, v)

    global_ris = sorted(all_ris, key=ri_sort_key)

    # Map RI → global index (k number)
    ri_to_index = {ri: i + 1 for i, ri in enumerate(global_ris)}

    print(f"\nTotal unique RI values: {len(global_ris)}")
    for ri in global_ris:
        print(f"  RI[{ri_to_index[ri]}] = {ri}")

    # === Build DataFrame with consistent global indexing ===
    rows = []
    for entry in per_file_data:
        pcap = entry["pcap_file"]
        counts = entry["ri_counts"]
        pkt_count = entry["packet_count"]

        row = {
            "pcap_file": pcap,
            "unique_RI_count": len(counts),
            "RI_packet_count": pkt_count
        }

        # Insert RI_i and k_i in global order
        for ri, idx in ri_to_index.items():
            row[f"RI_{idx}"] = ri
            row[f"k{idx}"] = counts.get(ri, 0)

        rows.append(row)

    df = pd.DataFrame(rows)

    # Sort by date
    df["capture_datetime"] = df["pcap_file"].apply(extract_date_from_filename)
    df = df.sort_values("capture_datetime").reset_index(drop=True)

    # Write Excel
    print(f"\nWriting Excel file to {OUTPUT_XLSX} ...")
    df.to_excel(OUTPUT_XLSX, index=False)

    # === Stacked bar plot ===
    k_columns = sorted([c for c in df.columns if re.match(r"^k\d+$", c)],
                       key=lambda x: int(x[1:]))

    if not k_columns:
        print("No k columns to plot.")
        return

    # Convert to numeric
    for c in k_columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df_plot = df[df[k_columns].sum(axis=1) > 0]

    if df_plot.empty:
        print("No data available for plotting.")
        return

    # Begin plotting
    plt.figure(figsize=(16, 8))
    cmap = cm.get_cmap("tab10")

    x = np.arange(len(df_plot))
    cumulative = np.zeros(len(df_plot))

    # Stacked bars
    for idx, col in enumerate(k_columns):
        color = cmap(idx % 10)
        plt.bar(
            x,
            df_plot[col].values,
            bottom=cumulative,
            color=color,
            label=col
        )
        cumulative += df_plot[col].values

    # X-axis labels (YYYY-MM-DD)
    x_labels = [Path(row["pcap_file"]).stem[:10] for _, row in df_plot.iterrows()]
    plt.xticks(
        x,
        x_labels,
        rotation=45,
        ha="right",
        fontsize=20,
        fontweight="bold"
    )

    plt.ylabel("RI Packet Count", fontsize=20, fontweight="bold")
    #plt.title("RI= Key usage - Device = Linkind-Matter-Plug", fontsize=24, fontweight="bold")

    # Legend
    plt.legend(
        title="Key",
        fontsize=16,
        title_fontsize=16,
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_HIST)
    print(f"Stacked histogram saved to {OUTPUT_HIST}")

    print("\nDone.")


if __name__ == "__main__":
    main()
