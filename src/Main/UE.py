from src.Main.utils import DataType_Bf, AntennaType, RequestDataType
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class UE:
    id_g: int = -1
    id_l: int = -1
    cell_id: int = -1
    loc: int = -1
    bf_sector: int = -1
    bf_vector: int = -1
    h_freq: float = -1
    num_antenna_elements: Tuple[int, int] = (8, 1)
    antenna_type: AntennaType = AntennaType.URA
    txpower: float = 10.0
    data_request_time_stamps: Optional[RequestDataType] = field(default_factory=list)

    def __post_init__(self):
        """
        Additional initialization logic for UE objects.
        """
        self.channel = DataType_Bf(
            bf_sector=self.bf_sector,
            bf_vector=self.bf_vector,
            h_freq=self.h_freq
        )

    def add_request_time_stamp(self, time_stamp: int):
        """
        Add a new data request time stamp to the UE's history.
        """
        self.data_request_time_stamps.append(time_stamp)
