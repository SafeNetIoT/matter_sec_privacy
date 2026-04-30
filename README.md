# Beyond the Hype: Empirical Analysis of the Matter Standard’s Security and Privacy

## Dataset Overview


This repository contains Wireshark packet captures collected from a diverse set of IoT devices across both Matter and non-Matter ecosystems, including smart plugs, lighting systems, bridges, and controllers.

All data were collected in a controlled laboratory environment under identical operating conditions. Traffic was captured at the network gateway, enabling consistent cross-device and cross-vendor comparisons.

### Supported analyses
- Protocol-level communication behavior
- Vendor-specific traffic characteristics
- Comparative analysis of Matter vs. legacy IoT ecosystems

## Data Collection Methodology
- Capture point: Network gateway (passive monitoring)
- Environment: Isolated test network
- Device state: Normal operation (on/off, idle, pairing where applicable)
- Tools: Wireshark / tcpdump

## Devices evaluated


### Non-Matter Devices 
(Legacy IoT Baseline)

| Device | Device | Device | Device | Device | Device |
|--------|--------|--------|--------|--------|--------|
| TP-Link Kasa bulb | Sengled bulb | Gosund bulb | Wiz bulb | Smartlife bulb | Yeelight bulb |
| Govee LED strip | Magic Home strip | — | — | — | — |
| TP-Link Kasa plug | Meross plug | Wemo plug | Amazon plug | Meross door opener | August lock |

### Matter Lights and Plugs  
(Matter-enabled devices across multiple vendors for interoperability analysis)

| Device | Device | Device | Device | Device | Device |
|--------|--------|--------|--------|--------|--------|
| TP-Link Tapo bulb | Sengled bulb | Linkind bulb | Orein bulb | Consciot bulb | Govee LED strip |
| TP-Link Tapo plug | Meross plug | Eightree plug | Sengled plug | Sailsco plug | Xenon plug |
| Moes plug | Tuya plug | Linkind plug | Cync plug | Leviton plug | UseeLink plug |

### Matter Bridging Devices  
(Devices used to integrate legacy IoT ecosystems into Matter-compatible networks)

| Device | Device | Device | Device | Device | Device |
|--------|--------|--------|--------|--------|--------|
| Aqara bridge | Aqara bridge M2 | SwitchBot bridge | Philips bridge | SmartLife bridge | Third Reality bridge |
| Meross bridge | — | — | — | — | — |

### Matter Controllers

| Controller | Controller | Controller | Controller |
|------------|------------|------------|------------|
| Apple HomePod Mini | Google Nest Mini | Amazon Echo | Aeotec SmartThings Hub |

Total devices: 35

### Data and Reproducibility

The dataset, code, and additional materials associated with this work are publicly available on Zenodo:

https://doi.org/10.5281/zenodo.19893703

The dataset consists of traffic captures collected from multiple devices, with each device represented by a separate `.pcap` file. The traces vary in size from approximately 85 MB to 300 MB.

Python scripts are provided to demonstrate example processing and analysis workflows, and can be used as a starting point for reproducing the results presented in the paper.



## RDI Rotation Analysis Scripts

This directory contains four Python scripts used to analyze Rotating Device Identifier (RDI) behaviour in mDNS traffic from Matter devices:

- `rdi-cync-smartplug-rotation.py`  
- `rdi-linkind-smartplug-rotation.py`  
- `rdi-tuya-smartplug-rotation.py`  
- `rdi-meross-hub-rotation.py`  

All four scripts implement the same analysis pipeline and differ only in the input datasets and output naming conventions.

---

### Purpose

These scripts quantify the rotation and usage patterns of RDI values (`RI=` fields) observed in mDNS TXT records, as used in the measurement methodology of the paper.

---

### Methodology

For each PCAP file, the scripts:

1. Extract mDNS packets containing TXT records using:
   - Filter: `udp.port == 5353 && dns.txt`
2. Parse TXT records to extract `RI=` values (hex-encoded identifiers)
3. Compute per-file metrics:
   - Number of unique RI values  
   - Total number of packets containing RI values  
   - Frequency of each RI value (occurrence counts)
4. Order RI values deterministically (numeric prefix where applicable)
5. Construct structured outputs:
   - `RI_1, RI_2, ...` (unique identifiers)
   - `k1, k2, ...` (corresponding packet counts)
6. Aggregate results across traces
7. Generate outputs:
   - Tabular dataset (Excel)
   - Grouped histogram of RI usage per trace

---

### Inputs

Each script requires manual configuration of:

- `PCAP_DIRS`: list of directories containing PCAP/PCAPNG files  

All PCAP files in the specified directories are processed automatically.  
No command-line interface is provided; paths are defined within the script.

---

### Outputs

For each dataset, the scripts produce:

- An Excel file (`.xlsx`) containing:
  - Per-trace RI values and counts  
  - Derived key suffixes (last 4 hex characters) for analysis  
- A grouped histogram (`.png`) showing RI usage across traces  
- Console output summarizing:
  - Number of unique RI values per trace  
  - Total unique RI values across all traces  

---

### Environment and Dependencies

Tested with:

- Python 3.x  
- `tshark` (Wireshark CLI, must be installed and in PATH)  
- `pandas`  
- `matplotlib`  
- `numpy`  

---

### Reproducibility Notes

- Packet parsing is performed using `tshark` to ensure consistent extraction of DNS TXT records.  
- RI extraction is based on regex matching of `RI=` fields within TXT payloads.  
- Results are deterministic given identical PCAP inputs.  
- File ordering is normalized using timestamps extracted from filenames where available.  
- The four scripts are interchangeable aside from dataset-specific configuration.



### mDNS Frequency Analysis Scripts

This directory contains four Python scripts used to analyze multicast DNS (mDNS) traffic from packet capture (PCAP) files:

mdns-eightree-ip4-ip6-freq.py
mdns-merosshub-ip4-ip6-freq.py
mdns-sailsco1-ip4-ip6-freq.py
mdns-sengled-ip4-ip6-freq.py

All four scripts implement the same analysis pipeline and differ only in the input datasets and output naming conventions.

Purpose

These scripts quantify the frequency of mDNS TXT response packets over IPv4 and IPv6, as used in the measurement methodology of the paper.

Methodology

For each PCAP file, the scripts:

Filter mDNS response packets containing TXT records using:
IPv4: dns.flags.response == 1 && dns.txt && ip.dst == 224.0.0.251
IPv6: dns.flags.response == 1 && dns.txt && ipv6.dst == ff02::fb
Extract packet timestamps
Compute per-file metrics:
Packet count
Trace duration
Inter-arrival time statistics (mean, min, max)
Packet frequency (packets/sec)
Compute averages across all input files
Generate summary plots:
Stacked bar chart (IPv4 vs IPv6 packet counts)
Frequency line plot per trace
Inputs

Each script requires manual configuration of:

PCAP_PATH: directory containing PCAP files
PCAP_FILES: list of PCAP filenames

No command-line interface is provided; paths are defined within the script.

Outputs

For each dataset, the scripts produce:

Console output with per-file and averaged statistics
Two figures saved locally:
<prefix>_packet_counts.png
<prefix>_frequency.png
Environment and Dependencies

Tested with:

Python 3.x
pyshark (requires tshark installed and in PATH)
matplotlib
Reproducibility Notes
The scripts process packets in a streaming manner (keep_packets=False) to reduce memory usage.
Results depend on the correctness of PCAP timestamps and prior capture setup.
No randomness is involved; given identical inputs, outputs are deterministic.
The four scripts are interchangeable aside from dataset-specific parameters.
### Relevance

This tool enables reproducible measurement of identifier behavior in Matter mDNS traffic, supporting analysis of identifier diversity, reuse, and potential privacy implications in IoT ecosystems.

