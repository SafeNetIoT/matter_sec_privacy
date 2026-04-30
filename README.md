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



### Example Analysis Scripts

This repository includes three sample Python scripts that demonstrate the analysis methodology used to investigate the Matter Rotating Device Identifier (RDI) behavior across different IoT devices.

Each script corresponds to a specific Matter-enabled device category:

- `Cync-Matter-Plug-New.py` — analysis of Cync Matter plug traffic patterns  
- `Linkind-Matter-Plug-New.py` — analysis of Linkind Matter plug communication behavior  
- `Tuya-Matter-Plug-New.py` — analysis of Tuya Matter plug traffic characteristics  

These scripts provide representative examples of the broader processing pipeline used in this study, including packet extraction, RI/RDI identification, and traffic-level feature analysis. They are intended to demonstrate reproducible methodology rather than exhaustive device coverage.

This repository includes a Python script for analyzing multicast DNS (mDNS) traffic within packet capture (PCAP/PCAPNG) files, with a focus on *Resource Identifier (RI)* values used in Matter device communications.
The script uses `tshark` to extract DNS TXT records from mDNS traffic and applies regex-based parsing to identify RI fields. For each capture, it computes the set of unique RI values and their frequency of occurrence, producing a structured dataset exported as an Excel file.
In addition, the script generates a grouped bar chart that visualizes RI usage across captures. Identifiers are color-coded using the last four hexadecimal characters, enabling clear comparison of identifier reuse and variation over time.

This tool supports reproducible, empirical analysis of identifier behavior in IoT network traces, aligning with measurement methodologies used in IMC/IEEE studies.


### Script opreation  

### RI Extraction and Analysis

For each PCAP trace, the script extracts RI values from mDNS DNS TXT records and computes per-trace statistics, including the set of unique RIs, their occurrence counts, and the total number of RI-bearing packets. RI values are deterministically ordered to ensure consistent indexing across traces.
To enable cross-trace comparison, each RI is mapped to a compact key defined by its last four hexadecimal characters. These keys provide stable identifiers for grouping and visualization.
Traces are temporally ordered using timestamps embedded in filenames, allowing analysis of RI usage over time.

### Output and Visualization

Results are exported as a structured `.xlsx` dataset containing per-trace RI values, frequencies, derived keys, and packet counts, supporting reproducibility and downstream analysis.

A grouped bar chart is generated to visualize RI distributions across traces, with color encoding based on RI suffixes. This highlights identifier reuse, distribution skew, and temporal variation. The figure is saved as a publication-ready image.



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

