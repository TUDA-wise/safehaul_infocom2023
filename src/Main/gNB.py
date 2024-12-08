from src.Main.utils import DataType_Bf


class Gnb:
    def __init__(self, id=-1, loc=-1, num_ue=0, num_antenna_elements=16, antenna_type="URA", txpower=10):
        '''
        Class for fiber gnb
        :param id: global id of gNB
        :param loc: global location of UE
        :param num_ue: number of UE connected to this gNB in this Cell
        '''
        self.id = id
        self.loc = loc
        self.num_ue = num_ue
        self.txpower = txpower
        self.num_antenna_elements = num_antenna_elements
        self.antenna_type = antenna_type
        self.channel_list = []

        for i in range(self.num_ue):
            self.channel_list.append(DataType_Bf())


class Iab:
    def __init__(self, id=-1, loc=-1, num_ue=0, num_antenna_elements=16, antenna_type="URA", txpower=30, tier=-1,
                 buffer_size=2000, total_pass_data=0, equiped_buffer=0, frw=-1, access_sc_list=[], access_exe_list=[],
                 access_req_list=[], bkh_sc_list=[], bkh_exe_list=[], bkh_req_list=[]):
        '''

        :param id: global id of gNB
        :param loc: global location of UE
        :param num_ue: number of UE connected to this gNB in this Cell
        '''
        self.id = id
        self.loc = loc
        self.num_ue = num_ue
        self.txpower = txpower
        self.num_antenna_elements = num_antenna_elements
        self.antenna_type = antenna_type
        self.channel_impulse_response_per_ue = []
        self.tier = tier
        self.buffer_size = buffer_size
        self.equiped_buffer = equiped_buffer
        self.access_sc_list = access_sc_list
        self.access_exe_list = access_exe_list
        self.access_req_list = access_req_list
        self.bkh_sc_list = bkh_sc_list
        self.bkh_exe_list = bkh_exe_list
        self.bkh_req_list = bkh_req_list
        self.frw = frw
        self.total_pass_data = total_pass_data
