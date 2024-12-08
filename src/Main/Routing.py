from src.Main.utils import distance_3d, PathDataType
from src.Main.gNB import Iab
import numpy as np
from typing import List, Tuple


def distance_aware_path_generation(
        iab_list: List[Iab],
        gnb_loc: np.ndarray,
        max_distance: float
) -> Tuple[np.ndarray, List[PathDataType]]:
    """
    :param gnb_loc: location of wired gnb
    :param iab_list: list contain all iab nodes location
    :param max_distance: max_distance that two iab or iab and gnb could communicate (meter)
    :return: path_matrix and path_list
    """
    if not iab_list or not isinstance(gnb_loc, np.ndarray):
        raise ValueError("Invalid inputs!")
    number_nodes = len(iab_list)
    path_matrix = np.zeros((len(iab_list), len(iab_list) + 1))
    path_list = []
    cnt = 0

    # Helper function to add paths
    def add_path(from_node: int, to_node: int):
        nonlocal cnt
        path_matrix[from_node, to_node] = 1
        path_list.append(
            PathDataType(
                path_id=cnt,
                from_node=from_node,
                to_node=to_node,
                sinr=np.random.randint(1, 20),
            )
        )
        cnt += 1

    # Connect IAB nodes to the gNB
    for node1 in range(number_nodes):
        if (dist_to_gnb := distance_3d(iab_list[node1].loc, gnb_loc)) < max_distance:
            add_path(node1, number_nodes)


    # Connect IAB nodes to each other
    for node1 in range(number_nodes - 1):
        dist_to_gnb1 = distance_3d(iab_list[node1].loc, gnb_loc)
        for node2 in range(node1 + 1, number_nodes):
            dist_between_nodes = distance_3d(iab_list[node1].loc, iab_list[node2].loc)
            if max_distance > dist_between_nodes > 0:
                dist_to_gnb2 = distance_3d(iab_list[node2].loc, gnb_loc)
                if dist_to_gnb1 < dist_to_gnb2:
                    add_path(node2, node1)
                else:
                    add_path(node1, node2)
    return path_matrix, path_list


# to do Some iab May not assign
def section_aware_path_generation(iab_list, max_distance):
    """

    :param gnb_loc: location of wired gnb
    :param iab_list: list contain all iab nodes location
    :param max_distance: max_distance that two iab or iab and gnb could communicate (meter)
    :return: path_matrix and path_list
    """

    number_nodes = len(iab_list)
    path_matrix = np.zeros((len(iab_list), len(iab_list) + 1))
    path_list = []
    cnt = 0

    # Helper function to add paths
    def add_path(from_node: int, to_node: int):
        nonlocal cnt
        path_matrix[from_node, to_node] = 1
        path_list.append(
            PathDataType(
                path_id=cnt,
                from_node=from_node,
                to_node=to_node,
                sinr=np.random.randint(1, 20),
            )
        )
        cnt += 1
    for node1 in range(0, number_nodes):
        if iab_list[node1].tier == 0:
            add_path(node1, number_nodes)
    filtered_pairs = [
        (node1, node2)
        for node1 in range(number_nodes)
        for node2 in range(node1 + 1, number_nodes)
        if abs(iab_list[node2].tier - iab_list[node1].tier) == 1
    ]

    for (node1, node2) in filtered_pairs:
        distance_node1_to_node2 = distance_3d(iab_list[node1].loc, iab_list[node2].loc)
        if distance_node1_to_node2 < max_distance and distance_node1_to_node2 != 0:
            if iab_list[node2].tier == iab_list[node1].tier - 1:
                add_path(node1, node2)
            else:
                add_path(node2, node1)

    return path_matrix, path_list
