from typing import List, Union
import numpy as np


def path_select_distance_sinr(possible_path_list: Union[int, List[int]], all_path_list: Union[int, List[int]]) -> int:
    """
    Select the path with the maximum SINR from a list of paths and return a single path directly.

    :param possible_path_list: Either a single path (integer) or a list of path indices.
    :return: Selected path index with the maximum SINR, or -1 if no valid path is found.
    """
    # Handle the case where path_list is a single integer
    if isinstance(possible_path_list, int):
        return possible_path_list if possible_path_list != -1 else -1

    # Find the path index with the maximum SINR
    try:
        path = max(
            (p for p in possible_path_list),
            key=lambda p: all_path_list[p].sinr
        )
    except (KeyError, AttributeError, IndexError) as e:
        # Log or handle errors related to accessing path_list
        print(f"Error during path selection: {e}")
        return -1

    return path


def path_select_rand(path_list: Union[int, List[int]]) -> int:
    """
    Select a random path from the list or return a single path directly.

    :param path_list: Either a single integer path or a list of path indices.
    :return: Selected path index, or -1 if no valid path exists.
    """
    # Handle case where path_list is an integer
    if isinstance(path_list, int):
        return path_list if path_list != -1 else -1

    # Handle case where path_list is a list
    if path_list and path_list[0] != -1:
        return np.random.choice(path_list)

    # If path_list is invalid or contains -1
    return -1


def round_robin_scheduler(sc_list, req_list, exe_list):
    """
    Implements a round-robin scheduler:
    - Handles requests from `req_list` and adds to `sc_list` with priority.
    - Processes tasks from `sc_list`, moves completed tasks to `exe_list`.

    :param sc_list: List of scheduled tasks.
    :param req_list: List of incoming requests.
    :param exe_list: List of executed tasks.
    :return: ID of the transmitted traffic (`tr_id`).
    """
    tr_id = None  # Default in case no task is processed

    # Handle requests
    if req_list:
        if len(req_list) > 1:
            # Ensure requests are from different UEs (Unique Entities)
            if any(req_list[0].id != req.id for req in req_list[1:]):
                while req_list[0].id == req_list[1].id:
                    req_list.append(req_list.pop(1))  # Rotate similar UEs to the end

        # Add the highest-priority request to `sc_list`
        sc_list.insert(0, req_list.pop(0))

    # Process the first scheduled task
    if sc_list:
        tr_id = sc_list[0].tr_id  # Get traffic ID of the current task
        exe_list.append(sc_list[0].id)  # Mark task as executed
        sc_list.pop(0)  # Remove the task from `sc_list`

    return tr_id
