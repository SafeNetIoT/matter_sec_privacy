import os
import pyshark
import matplotlib.pyplot as plt
import gc

# =========================
# USER PARAMETERS
# =========================
PCAP_PATH = r"D:\Matter\Eightree1"

PCAP_FILES = [
    "2025-03-03_14.51.26_10.13.0.156.pcap",
    "2025-02-27_14.50.27_10.13.0.156.pcap",
    "2025-01-29_14.45.28_10.13.0.156.pcap",
    "2025-01-25_09.28.18_10.13.0.156.pcap",
    "2025-01-23_09.27.29_10.13.0.156.pcap"
]

OUTPUT_PREFIX = "eightree1"

# =========================
# SAFE CAPTURE
# =========================
def get_capture(file_path, filter_str):
    return pyshark.FileCapture(
        file_path,
        display_filter=filter_str,
        keep_packets=False,
        use_json=True
    )

# =========================
# EXTRACT TIMES
# =========================
def extract_times(capture):
    times = []
    try:
        for pkt in capture:
            try:
                times.append(float(pkt.sniff_timestamp))
            except:
                continue
    except:
        pass
    finally:
        try:
            capture.close()
        except:
            pass

    return sorted(times)

# =========================
# ANALYZE SINGLE FILE
# =========================
def analyze_times(times):
    if len(times) < 2:
        return None

    duration = times[-1] - times[0]
    gaps = [t2 - t1 for t1, t2 in zip(times[:-1], times[1:])]

    return {
        "count": len(times),
        "duration": duration,
        "avg_gap": sum(gaps) / len(gaps),
        "min_gap": min(gaps),
        "max_gap": max(gaps),
        "frequency": len(times) / duration if duration > 0 else 0
    }

# =========================
# PRINT PER FILE
# =========================
def print_file_results(result, label, filename):
    print(f"\n--- {label} RESULTS for {filename} ---")

    if not result:
        print("No valid data")
        return

    print(f"Packet count: {result['count']}")
    print(f"Duration: {result['duration']:.2f} sec")
    print(f"Avg gap: {result['avg_gap']:.2f} sec")
    print(f"Min gap: {result['min_gap']:.4f} sec")
    print(f"Max gap: {result['max_gap']:.2f} sec")
    print(f"Frequency: {result['frequency']:.4f} packets/sec")
    print(f"Packets per minute: {result['frequency'] * 60:.2f}")

# =========================
# PROCESS ALL FILES
# =========================
ipv4_results = []
ipv6_results = []

ipv4_counts = []
ipv6_counts = []

ipv4_freqs = []
ipv6_freqs = []

labels = []

for file in PCAP_FILES:
    full_path = os.path.join(PCAP_PATH, file)
    print(f"\nProcessing: {file}")

    labels.append(file)

    # IPv4
    cap4 = get_capture(
        full_path,
        "dns.flags.response == 1 && dns.txt && ip.dst == 224.0.0.251"
    )
    times4 = extract_times(cap4)
    del cap4

    result4 = analyze_times(times4)
    if result4:
        ipv4_results.append(result4)
        ipv4_counts.append(result4["count"])
        ipv4_freqs.append(result4["frequency"])
        print_file_results(result4, "IPv4", file)
    else:
        ipv4_counts.append(0)
        ipv4_freqs.append(0)

    # IPv6
    cap6 = get_capture(
        full_path,
        "dns.flags.response == 1 && dns.txt && ipv6.dst == ff02::fb"
    )
    times6 = extract_times(cap6)
    del cap6

    result6 = analyze_times(times6)
    if result6:
        ipv6_results.append(result6)
        ipv6_counts.append(result6["count"])
        ipv6_freqs.append(result6["frequency"])
        print_file_results(result6, "IPv6", file)
    else:
        ipv6_counts.append(0)
        ipv6_freqs.append(0)

# =========================
# AVERAGING FUNCTION
# =========================
def average_results(results, label):
    print(f"\n===== {label} AVERAGED RESULTS =====")

    if not results:
        print("No valid data")
        return

    n = len(results)

    avg_count = sum(r["count"] for r in results) / n
    avg_duration = sum(r["duration"] for r in results) / n
    avg_gap = sum(r["avg_gap"] for r in results) / n
    avg_min_gap = sum(r["min_gap"] for r in results) / n
    avg_max_gap = sum(r["max_gap"] for r in results) / n
    avg_freq = sum(r["frequency"] for r in results) / n

    print(f"Files processed: {n}")
    print(f"Avg packet count: {avg_count:.2f}")
    print(f"Avg duration: {avg_duration:.2f} sec")
    print(f"Avg gap: {avg_gap:.2f} sec")
    print(f"Avg min gap: {avg_min_gap:.4f} sec")
    print(f"Avg max gap: {avg_max_gap:.2f} sec")
    print(f"Avg frequency: {avg_freq:.4f} packets/sec")
    print(f"Packets per minute: {avg_freq * 60:.2f}")

# =========================
# PLOTTING
# =========================
def plot_counts(labels, ipv4_counts, ipv6_counts):
    x = range(len(labels))

    plt.figure()
    plt.bar(x, ipv4_counts)
    plt.bar(x, ipv6_counts, bottom=ipv4_counts)

    plt.xticks(x, labels, rotation=45, ha='right')
    plt.ylabel("Packet Count")
    plt.title(f"{OUTPUT_PREFIX} mDNS TXT Packet Count per File")

    plt.tight_layout()
    filename = f"{OUTPUT_PREFIX}_packet_counts.png"
    plt.savefig(filename)
    print(f"Saved: {filename}")

    plt.show()

def plot_frequency(labels, ipv4_freqs, ipv6_freqs):
    x = range(len(labels))

    plt.figure()
    plt.plot(x, ipv4_freqs, marker='o')
    plt.plot(x, ipv6_freqs, marker='o')

    plt.xticks(x, labels, rotation=45, ha='right')
    plt.ylabel("Packets per Second")
    plt.title(f"{OUTPUT_PREFIX} mDNS Frequency per File")

    plt.tight_layout()
    filename = f"{OUTPUT_PREFIX}_frequency.png"
    plt.savefig(filename)
    print(f"Saved: {filename}")

    plt.show()

# =========================
# FINAL OUTPUT
# =========================
average_results(ipv4_results, "IPv4")
average_results(ipv6_results, "IPv6")

plot_counts(labels, ipv4_counts, ipv6_counts)
plot_frequency(labels, ipv4_freqs, ipv6_freqs)

# Cleanup
gc.collect()