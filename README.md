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

## Data Availability
The raw packet capture traces used in this study are available via the [PCAP Dataset]

All network traces follow a consistent directory structure:
data/<category>/<device-name>/network_traces


## Repository Structure

### mDNS RI Analysis Script

This repository includes a Python script for analyzing multicast DNS (mDNS) traffic within packet capture (PCAP/PCAPNG) files, with a focus on *Resource Identifier (RI)* values used in Matter device communications.
The script uses `tshark` to extract DNS TXT records from mDNS traffic and applies regex-based parsing to identify RI fields. For each capture, it computes the set of unique RI values and their frequency of occurrence, producing a structured dataset exported as an Excel file.
In addition, the script generates a grouped bar chart that visualizes RI usage across captures. Identifiers are color-coded using the last four hexadecimal characters, enabling clear comparison of identifier reuse and variation over time.

This tool supports reproducible, empirical analysis of identifier behavior in IoT network traces, aligning with measurement methodologies used in IMC/IEEE studies.


### RI Extraction and Analysis

For each PCAP trace, the script extracts RI values from mDNS DNS TXT records and computes per-trace statistics, including the set of unique RIs, their occurrence counts, and the total number of RI-bearing packets. RI values are deterministically ordered to ensure consistent indexing across traces.
To enable cross-trace comparison, each RI is mapped to a compact key defined by its last four hexadecimal characters. These keys provide stable identifiers for grouping and visualization.
Traces are temporally ordered using timestamps embedded in filenames, allowing analysis of RI usage over time.

### Output and Visualization

Results are exported as a structured `.xlsx` dataset containing per-trace RI values, frequencies, derived keys, and packet counts, supporting reproducibility and downstream analysis.

A grouped bar chart is generated to visualize RI distributions across traces, with color encoding based on RI suffixes. This highlights identifier reuse, distribution skew, and temporal variation. The figure is saved as a publication-ready image.

### Relevance

This tool enables reproducible measurement of identifier behavior in Matter mDNS traffic, supporting analysis of identifier diversity, reuse, and potential privacy implications in IoT ecosystems.

## Data and Reproducibility

The dataset, code, and additional materials associated with this work are publicly available on Zenodo:

https://doi.org/10.5281/zenodo.19885775
