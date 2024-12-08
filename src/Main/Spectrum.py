# SINR to CQI mapping table (example values, replace with Table 7g values)
SINR_to_CQI = {
    -5: 1,  # Example: SINR of -5 dB maps to CQI 1
    0: 5,  # SINR of 0 dB maps to CQI 5
    5: 10,  # SINR of 5 dB maps to CQI 10
    10: 15  # SINR of 10 dB maps to CQI 15
}

# CQI to spectral efficiency (SE) mapping table (replace with actual table values)
CQI_to_SE = {
    1: 0.1523,  # Example spectral efficiency for CQI 1
    5: 0.8770,  # Spectral efficiency for CQI 5
    10: 2.4063,  # Spectral efficiency for CQI 10
    15: 4.5234  # Spectral efficiency for CQI 15
}


def calculate_data_rate(sinr, bandwidth_mhz, resource_blocks):
    """
    Calculate data rate based on SINR.

    Parameters:
    - sinr: Signal-to-Interference-plus-Noise Ratio (dB)
    - bandwidth_mhz: Total bandwidth in MHz
    - resource_blocks: Number of resource blocks available

    Returns:
    - Data rate in Mbps
    """
    # Map SINR to CQI
    cqi = max([k for k in SINR_to_CQI if sinr >= k], default=1)
    cqi = SINR_to_CQI[cqi]

    # Get spectral efficiency (SE) from CQI
    se = CQI_to_SE.get(cqi, 0)

    # Calculate data rate
    rb_bandwidth = bandwidth_mhz / resource_blocks  # Bandwidth per RB in MHz
    data_rate = se * resource_blocks * rb_bandwidth * 1000  # Mbps
    return data_rate
