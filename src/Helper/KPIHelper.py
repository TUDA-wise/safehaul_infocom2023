import numpy as np


def post_processing(network_model):
    # Print total received and generated packets
    print("Total received packets:", len(network_model.traffic_list_total))
    print("Total generated packets:", len(network_model.traffic_list_temp))

    # Calculate and print average throughput per UE
    avg_thr = (
        (network_model.packet_size / network_model.num_ue)
        * len(network_model.traffic_list_total)
        * (1000 / network_model.simulation_time_steps)
    )
    print("Avg throughput per UE [Mbps]:", avg_thr)

    # Calculate and sort pass data for each cell
    pass_data = np.array([cell.total_pass_data for cell in network_model.iab_list])
    sorted_indices = np.argsort(pass_data)[::-1]
    print("Packets indices in each Cell:", sorted_indices)
    print("Packets in each Cell:", pass_data[sorted_indices])

    # Calculate total load per node
    total_load = pass_data.tolist()
    print("Total load per each node:", total_load)

    # Calculate latency for each traffic item
    latency_list = [
        traffic.stop_time - traffic.start_time for traffic in network_model.traffic_list_total
    ]
    print("Avg Backhual latency [ms]:", np.mean(latency_list))

