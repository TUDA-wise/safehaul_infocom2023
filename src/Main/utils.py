import math
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from termcolor import colored
from dataclasses import dataclass
from src.Main.Spectrum import calculate_data_rate
from enum import Enum


@dataclass
class RequestDataType:
    id: int = -1
    data: int = -1
    time: int = -1
    tr_id: int = -1


class DataType_Bf:
    def __init__(self, bf_sector=-1, bf_vector=-1, h_freq=-1):
        self.bf_sector = bf_sector
        self.bf_vector = bf_vector
        self.h_freq = h_freq


# path data type
class PathDataType:
    def __init__(self, path_id=-1, from_node=-1, to_node=-1, b_v_1=-1, b_v_2=-1, sinr=-1, path_equiped=0, bw=40,
                 resource_blocks=-1):
        self.path_rate = None
        self.bw = bw
        self.resource_blocks = resource_blocks
        self.path_id = path_id
        self.from_node = from_node
        self.to_node = to_node
        self.b_v_1 = b_v_1
        self.b_v_2 = b_v_2
        self.sinr = sinr
        self.path_equiped = path_equiped
        self.calc_path_rate()

    def calc_path_rate(self):
        self.path_rate = calculate_data_rate(self.sinr, self.bw, self.resource_blocks)

    def Set_path_rate(self, path_rate):
        self.path_rate = path_rate

    def Set_path_sinr(self, sinr):
        self.sinr = sinr


class TrafficDataType:
    def __init__(self, t_id=-1, ue_g_id=-1, cell_id=-1, path_list=None, start_time=-1, stop_time=-1, iab_node=-1,
                 subframe=-1, frame_count=-1, last_subframe=-1, access_region=-1, bkh_region=-1, data_size=-1):
        self.t_id = t_id
        self.ue_g_id = ue_g_id
        self.cell_id = cell_id
        self.path_list = path_list
        self.start_time = start_time
        self.stop_time = stop_time
        self.iab_node = iab_node
        self.subframe = subframe
        self.frame_count = frame_count
        self.last_subframe = last_subframe
        self.access_region = access_region
        self.bkh_region = bkh_region
        self.data_size = data_size


class AntennaType(Enum):
    URA = "URA"
    OTHER = "Other"  # Add other antenna types if necessary.


def logging(mode, message):
    if mode == "debug":
        print(message)


def distance_3d(loc1, loc2):
    '''
    calculate 3d distance between two nodes
    :param loc1: first node location
    :param loc2: second node location
    :return: distance (m)
    '''
    return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2 + (loc1[2] - loc2[2]) ** 2)




def plot_log_policy(gnb_loc, iab_list, path_list):
    """
    Visualizes the network topology by plotting IAB points, gNB, and connecting paths.

    :param gnb_loc: Coordinates of the gNB (tuple: x, y)
    :param iab_list: List of IAB points, each with a `loc` attribute containing coordinates
    :param path_list: List of paths, each with `from_node` and `to_node` attributes
    """
    gnb_id = len(iab_list)
    plt.figure(figsize=(15, 10))

    # Draw IAB points
    for cnt, points in enumerate(iab_list):
        plt.plot(points.loc[0], points.loc[1], marker="^", markersize=15, color="r",
                 label="IAB nodes" if cnt == 0 else "")
        plt.text(points.loc[0] + 15, points.loc[1] + 14, s=str(cnt), fontsize=12, color='r')

    # Draw gNB
    plt.plot(gnb_loc[0], gnb_loc[1], marker="^", markersize=20, color="g", label="IAB Donor")
    plt.text(gnb_loc[0] - 9, gnb_loc[1] - 9, s="Donor", fontsize=12, color="g")

    # Draw paths
    for i, path in enumerate(path_list):
        if path.to_node != gnb_id:
            from_node = iab_list[path.from_node].loc
            to_node = iab_list[path.to_node].loc
        else:
            from_node = iab_list[path.from_node].loc
            to_node = gnb_loc

        plt.arrow(from_node[0], from_node[1],
                  to_node[0] - from_node[0], to_node[1] - from_node[1],
                  color="y", length_includes_head=True, head_width=3, head_length=3)

        # Label the path with its index
        mid_x = (from_node[0] + to_node[0]) / 2
        mid_y = (from_node[1] + to_node[1]) / 2
        plt.text(mid_x, mid_y, s=str(i), fontsize=12, color="y")

    # Add legend and save the plot
    plt.legend(loc="upper right")
    plt.savefig("IABlocationsPath.png")


def step_by_step_visulaizer(num_cell, mode, Nk, Pk, Bk, achievable_rates_per_path_list):
    """
    Visualizes step-by-step cell data by logging relevant information in a consistent format.

    :param Nk: Neighborhood sets of IAB who IAB could communicate (possible IAB nodes)
    :param Pk: Links to the neighborhood sets of IAB who IAB could communicate (possible paths)
    :param Bk: Backhual Accumulated load
    :param achievable_rates_per_path_list: List of achievable rates per cell path
    """
    attributes = ['bold']
    for cell in range(num_cell):
        logging(mode, colored(f"Cell id: {cell}", 'red', attrs=attributes))

        # Consolidate repeated data logging
        cell_data = {
            "Bk": Bk[cell],
            "Nk": Nk[cell],
            "Pk": Pk[cell],
            "Achievable rates": achievable_rates_per_path_list[cell]
        }

        for label, value in cell_data.items():
            logging(mode, colored(f"{label}: {value}", 'red'))
