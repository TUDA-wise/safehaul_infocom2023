import numpy as np
from termcolor import colored
from src.Main.utils import logging, RequestDataType, step_by_step_visulaizer, TrafficDataType, distance_3d, \
    plot_log_policy
from src.Helper.TopologyHelper import topology_gen
from src.Main.gNB import Iab
from src.Main.UE import UE
from src.Main.Scheduler import path_select_rand, path_select_distance_sinr, round_robin_scheduler
from src.Main.Routing import distance_aware_path_generation, section_aware_path_generation
from src.Sionna.Channel import channel


class Simulator:
    def __init__(self, topology="Padova", channel_update_ON =False, num_ue=0, path_policy="section_aware", bs_height=15, ue_height=2,
                 simulation_time_steps=1000, packet_size=5, source_rate=100, mode="debug", scheduler="mlr", rngRun=42,
                 num_ut_ant=2, num_bs_ant=8, carrier_frequency=3.5e9, ebno_db=10, tx_power_dbm=41):
        self.rngRun = rngRun
        np.random.seed = self.rngRun

        self.num_ut_ant = num_ut_ant
        self.num_bs_ant = num_bs_ant
        self.tx_power_dbm = tx_power_dbm
        self.ebno_db = ebno_db
        self.carrier_frequency = carrier_frequency
        self.scheduler = scheduler
        self.packet_size = packet_size
        self.mode = mode  # "run" or "debug"
        self.simulation_time_steps = simulation_time_steps
        self.traffic_list_total = []
        self.traffic_list_temp = []
        self.source_rate = source_rate
        self.channel_update_ON = channel_update_ON
        self.gnb_loc = None
        self.topology = topology
        self.path_policy = path_policy
        self.num_ue = num_ue
        self.data_rate = 10  # mb
        self.num_cell = 0
        self.max_distance = 190
        self.bandwidth_mhz = 40
        self.resource_blocks = 255
        self.bs_height = bs_height
        self.ue_height = ue_height
        self.ue_list = []
        self.iab_list = []
        self.gnb_list = []
        # init ue(s),Iab(s) based on topology
        self.cell_init()
        self.BK = np.zeros((self.simulation_time_steps, self.num_cell))
        self.path_matrix = np.zeros((len(self.iab_list), len(self.iab_list) + 1))
        self.path_list = []
        # bkh path generation
        self.pre_run_filter_path_generation()
        self.Bachkul_channel_update()
        self.generated_packet = np.zeros(self.num_cell)

    def log(self, message):
        logging(self.mode, message)

    def cell_init(self):
        ''''
        in charge of initiate the cell based on topology
        '''
        self.log("Cell Init Started ...")
        self.gnb_loc, iab_nodes_loc_list = topology_gen(self.topology, self.bs_height)
        self.num_cell = len(iab_nodes_loc_list)
        self.iab_init(iab_nodes_loc_list)
        self.ue_init()
        self.log("Cell Init done!!!")

    def ue_init(self):
        '''
        initate Ue : drop in map and attach to the closested IAB
        '''
        for i in range(self.num_ue):
            # loc = tf.expand_dims(tf.convert_to_tensor(np.tile(np.array((np.random.rand()*150,np.random.rand()*150,self.ue_height)),(1,1)), dtype=tf.float32),axis=1)
            if self.topology == "smallMap":
                loc = np.tile(np.array((np.random.rand() * 340 + 20, np.random.rand() * 340 + 20, self.ue_height)),
                              (1, 1))
            else:
                loc = np.tile(np.array((np.random.rand() * 1700 + 300, np.random.rand() * 1800 + 400, self.ue_height)),
                              (1, 1))
            cell_id = self.attachment_ue_iab(loc)
            times_per_transmit = int((self.simulation_time_steps * self.source_rate) / (self.packet_size * 1000))
            traffic_request_time_steps = np.random.randint(0, self.simulation_time_steps - 100, int(times_per_transmit))
            self.ue_list.append(UE(id_g=i, id_l=self.iab_list[cell_id].num_ue, cell_id=cell_id, loc=loc,
                                   data_request_time_stamps=RequestDataType(i, self.packet_size,
                                                                            traffic_request_time_steps)))
            self.iab_list[cell_id].num_ue += 1
            self.log("Ue init with the id_g:" + str(self.ue_list[-1].id_g) + ",local id:" + str(
                self.ue_list[-1].id_l) + ", in cell:" + str(self.ue_list[-1].cell_id) + ",in loc:" + str(
                self.ue_list[-1].loc) + " with time stamp request list of:" + str(
                self.ue_list[-1].data_request_time_stamps.time))
            self.log("number of ue(s) in cell " + str(cell_id) + ", is:" + str(self.iab_list[cell_id].num_ue))

    def iab_init(self, iab_nodes_loc_list):
        for i in range(self.num_cell):
            d = distance_3d(iab_nodes_loc_list[i], self.gnb_loc)
            tier = d // self.max_distance
            # if tier == 0:
            #     self.path_matrix[i, self.num_cell] = 1
            self.iab_list.append(Iab(id=i, loc=iab_nodes_loc_list[i], tier=tier, access_sc_list=[], access_exe_list=[],
                                     access_req_list=[], bkh_exe_list=[], bkh_req_list=[], bkh_sc_list=[]))
            self.log("IAB node init with id:" + str(self.iab_list[-1].id) + " ,loc:" + str(
                self.iab_list[-1].loc) + ", in sector:" + str(self.iab_list[-1].tier))

    def attachment_ue_iab(self, loc: list[float]) -> int:
        return min(
            range(len(self.iab_list)),
            key=lambda i: distance_3d(self.iab_list[i].loc, loc[0])
        )

    def pre_run_filter_path_generation(self):
        if self.path_policy == "section_aware":
            self.path_matrix, self.path_list = section_aware_path_generation(self.iab_list, self.max_distance)
        elif self.path_policy == "distance_base":
            self.path_matrix, self.path_list = distance_aware_path_generation(self.iab_list, self.gnb_loc,
                                                                              self.max_distance)
        else:
            raise ValueError("not define policy")

        self.bandwidth_mhz = 40
        self.resource_blocks = 255
        plot_log_policy(self.gnb_loc, self.iab_list, self.path_list)
        self.log("path generation policy:" + self.path_policy + " done!")
        self.log(str(len(self.path_list)) + " paths generated")

    def Bachkul_channel_update(self):
        for path in self.path_list:
            if path.to_node != len(self.iab_list):
                from_node = self.iab_list[path.from_node].loc
                to_node = self.iab_list[path.to_node].loc
            else:
                from_node = self.iab_list[path.from_node].loc
                to_node = self.gnb_loc

            tmp_ch = channel(tx_power_dbm=self.tx_power_dbm, num_bs_ant=self.num_bs_ant, num_ut_ant=self.num_ut_ant,
                             ebno_db=self.ebno_db, loc_rx=to_node, loc_tx=from_node)
            tmp_ch.set_seed(self.rngRun)  # Set same rngRun to reproduce same value
            sinr, path_rate = tmp_ch.calc_channel_snr_data_rate()
            path.Set_path_sinr(sinr)
            path.Set_path_rate(path_rate)

    def possible_paths_for_traffic(self, iab_node):
        # self.log(" possible paths for traffic generated")
        possible_path = []
        possible_cells = np.squeeze(np.array(np.where(self.path_matrix[iab_node] == 1))).tolist()
        if isinstance(possible_cells, int):  # Ensure consistency in data type
            possible_cells = [possible_cells]
            # Generate possible paths
        possible_path = [
            path.path_id
            for cell in possible_cells
            for path in self.path_list
            if path.from_node == iab_node and path.to_node == cell
        ]

        return np.array(possible_cells), np.array(possible_path)

    def fronthaul_network(self, time_step):
        self.log("access network on progress, time step:" + str(time_step))
        # 1- check the new traffics and add to traffic_list_temp
        for ue in self.ue_list:
            if time_step in ue.data_request_time_stamps.time:
                # for i in range (int(ue.data_request_time_stamps.data/self.data_rate)):
                self.traffic_list_temp.append(
                    TrafficDataType(t_id=len(self.traffic_list_temp) + 1, ue_g_id=ue.id_g, cell_id=ue.cell_id,
                                    start_time=time_step,
                                    frame_count=int(ue.data_request_time_stamps.data / self.data_rate), subframe=0,
                                    iab_node=ue.cell_id, access_region=1, path_list=[],
                                    data_size=ue.data_request_time_stamps.data))
                self.iab_list[ue.cell_id].access_req_list.insert(0, RequestDataType(id=ue.id_g,
                                                                                    data=ue.data_request_time_stamps.data,
                                                                                    tr_id=self.traffic_list_temp[
                                                                                        -1].t_id))
                self.log("ue global id:" + str(ue.id_g) + ", local id:" + str(ue.id_l) + " ,in time step:" + str(
                    time_step) + " ,request traffic in cell:" + str(ue.cell_id) + " ,with the traffic id:" + str(
                    self.traffic_list_temp[-1].t_id) + " the data rate:" + str(ue.data_request_time_stamps.data))
                self.generated_packet[ue.cell_id] += 1

        # 2- scheduling for each cell Access and associate the traffic must transmit
        for cell in range(self.num_cell):

            if len(self.iab_list[cell].access_sc_list) != 0 or len(self.iab_list[cell].access_req_list) != 0:
                self.log(str(cell))
                tr_id_schedule = round_robin_scheduler(self.iab_list[cell].access_sc_list,
                                                       self.iab_list[cell].access_req_list,
                                                       self.iab_list[cell].access_exe_list)
                self.log(str(len(self.iab_list[cell].access_sc_list)))
                self.log(str(len(self.iab_list[cell].access_req_list)))
                self.log("trafic id:" + str(tr_id_schedule) + "  ,has been lunched in access of CELL:" + str(cell))
                # self.log(" exe list:"+str(self.iab_list[cell].access_exe_list))

                # launch traffic
                self.log(
                    "traffic :" + str(tr_id_schedule) + " has been lunched from access region to bkh in cell:" + str(
                        cell))
                tr_row = -1
                for i in range(len(self.traffic_list_temp)):
                    if self.traffic_list_temp[i].t_id == tr_id_schedule:
                        tr_row = i
                if tr_row == -1:
                    raise ValueError("traffic not found")
                self.traffic_list_temp[tr_row].access_region = 0
                self.traffic_list_temp[tr_row].bkh_region = 1
                # self.log(colored("buffer size of cell:"+str(self.traffic_list_temp[tr_row].iab_node)+",is:"+str(self.iab_list[ self.traffic_list_temp[tr_row].iab_node].equiped_buffer), 'red', attrs=['bold']))
                self.iab_list[cell].equiped_buffer += self.traffic_list_temp[tr_row].data_size
                self.iab_list[cell].total_pass_data += self.traffic_list_temp[tr_row].data_size
                # self.log(colored("Updated:buffer size of cell:"+str(self.traffic_list_temp[tr_row].iab_node)+",is:"+str(self.iab_list[ self.traffic_list_temp[tr_row].iab_node].equiped_buffer), 'red', attrs=['bold']))
                self.iab_list[cell].bkh_req_list.insert(0,
                                                        RequestDataType(data=self.traffic_list_temp[tr_row].data_size,
                                                                        tr_id=tr_id_schedule))

    def bakh_step_one(self):
        Nk = []  # neighborhood sets of IAB who IAB could communicate (possible IAB nodes)
        Pk = []  # links to the neighborhood sets of IAB who IAB could communicate (possible paths)
        Bk = []
        achivable_rates_per_path_list = []
        for cell in range(self.num_cell):
            achiveble_rate = []
            if len(self.iab_list[cell].bkh_sc_list) != 0 or len(self.iab_list[cell].bkh_req_list) != 0:
                possible_cell_list, possible_path_list = self.possible_paths_for_traffic(cell)
                self.log(colored("cell id:" + str(cell) + ",possible_cell_list:" + str(
                    possible_cell_list) + ",possible path list:" + str(
                    possible_path_list) + ", equiped_buffer of cell:" + str(self.iab_list[cell].equiped_buffer),
                                 'green', attrs=['bold']))
                for path in possible_path_list:
                    for p in range(len(self.path_list)):
                        if self.path_list[p].path_id == path:
                            achiveble_rate.append(self.path_list[p].path_rate)

                Pk.append(possible_path_list)
                Nk.append(possible_cell_list)
            else:
                self.log(colored(
                    "cell id:" + str(cell) + ", equiped_buffer of cell:" + str(self.iab_list[cell].equiped_buffer),
                    'green', attrs=['bold']))
                Pk.append(-1)
                Nk.append(-1)

            Bk.append(self.iab_list[cell].equiped_buffer)
            achivable_rates_per_path_list.append(achiveble_rate)
        return Nk, Pk, Bk, achivable_rates_per_path_list

    def bakh_data_pre_process(self, i):
        Nk = []  # neighborhood sets of IAB who IAB could communicate (possible IAB nodes)
        Pk = []  # links to the neighborhood sets of IAB who IAB could communicate (possible paths)
        Bk = []

        achivable_rates_per_path_list = []
        for cell in range(self.num_cell):
            achiveble_rate = []
            possible_cell_list, possible_path_list = self.possible_paths_for_traffic(cell)
            # self.log(colored("cell id:" + str(cell) + ",possible_cell_list:"+str(possible_cell_list)+",possible path list:"+ str(possible_path_list) +", equiped_buffer of cell:" +str( self.iab_list[cell].equiped_buffer), 'green', attrs=['bold']))
            for path in possible_path_list:
                for p in range(len(self.path_list)):
                    if self.path_list[p].path_id == path:
                        achiveble_rate.append(self.path_list[p].path_rate)

            Pk.append(possible_path_list)
            Nk.append(possible_cell_list)
            Bk.append(len(self.iab_list[cell].bkh_sc_list) + len(self.iab_list[cell].bkh_req_list))
            # Bk.append(self.iab_list[cell].equiped_buffer)
            self.BK[i, cell] = self.iab_list[cell].equiped_buffer
            self.log(colored("Bk:" + str(Bk) + ", in cell" + str(cell), 'blue'))
            # print(colored("Bk:" +str(Bk) + ", in cell" +str(cell), 'blue'))
            achivable_rates_per_path_list.append(achiveble_rate)

        return Nk, Pk, Bk, achivable_rates_per_path_list

    def bakh_scheduler(self, possible_path_list_total, Nk, Bk, achivable_rates_per_path_list):
        path_id_s = []
        cond_vector = []
        for cell in range(self.num_cell):
            path_id_s.append(path_select_distance_sinr(possible_path_list_total[cell], self.path_list))

            if path_id_s[-1] != -1:
                cond_vector.append(1)
            else:
                cond_vector.append(2)

        return path_id_s, cond_vector

    def bakh_step_two(self, time_step, path_id_s, cond_vector):
        for cell in range(self.num_cell):
            self.log("cell:" + str(cell) + ",path_id_s:" + str(path_id_s[cell]) + ",cond:" + str(cond_vector[cell]))
            # needs to transmit
            # import pdb; pdb.set_trace()
            if cond_vector[cell] == 1:
                path_id = path_id_s[cell]
                path = -1
                # print("path id:",path_id)
                for i in range(len(self.path_list)):
                    # self.log(str(self.path_list[i].path_id))
                    if self.path_list[i].path_id == path_id:
                        path = i
                if path == -1:
                    raise ValueError("path not found")
                self.path_list[path].path_equiped = 0
                while self.path_list[path].path_rate - self.path_list[path].path_equiped > 0 and (
                        len(self.iab_list[cell].bkh_sc_list) != 0 or len(self.iab_list[cell].bkh_req_list) != 0):
                    # print("before:",len(self.iab_list[cell].bkh_req_list))
                    t_id = round_robin_scheduler(self.iab_list[cell].bkh_sc_list, self.iab_list[cell].bkh_req_list,
                                                 self.iab_list[cell].bkh_exe_list)
                    # print("After:",len(self.iab_list[cell].bkh_req_list))
                    self.log("traffic id:" + str(t_id) + ", is selected to pass from cell:" + str(cell))
                    traffic = -1
                    for i in range(len(self.traffic_list_temp)):
                        if self.traffic_list_temp[i].t_id == t_id:
                            traffic = i
                    if traffic == -1:
                        raise ValueError("traffic not found")
                    if self.traffic_list_temp[traffic].data_size < self.path_list[path].path_rate - self.path_list[
                        path].path_equiped:
                        self.path_list[path].path_equiped += self.traffic_list_temp[traffic].data_size
                        # self.log(colored("buffer size of cell:"+str(cell)+",is:"+str(self.iab_list[cell].equiped_buffer), 'blue', attrs=['bold']))
                        # self.log(colored("equipeed buffer size of path:"+str(path_id)+",is:"+str(self.path_list[path].path_equiped), 'blue', attrs=['bold']))

                        # update traffic & iab_buffer size
                        self.traffic_list_temp[traffic].path_list.append(path)
                        self.log(colored(
                            "buffer size of cell:" + str(self.traffic_list_temp[traffic].iab_node) + ",is:" + str(
                                self.iab_list[self.traffic_list_temp[traffic].iab_node].equiped_buffer), 'green',
                            attrs=['bold']))
                        self.iab_list[self.traffic_list_temp[traffic].iab_node].equiped_buffer -= \
                            self.traffic_list_temp[traffic].data_size
                        self.log(colored("updated:buffer size of cell:" + str(
                            self.traffic_list_temp[traffic].iab_node) + ",is:" + str(
                            self.iab_list[self.traffic_list_temp[traffic].iab_node].equiped_buffer), 'green',
                                         attrs=['bold']))
                        self.traffic_list_temp[traffic].iab_node = self.path_list[path].to_node
                        # self.log("traffic id:" +str(t_id) +"is move from cell:"+str(cell)+", to cell id:" +str (self.traffic_list_temp[traffic].iab_node) +", by path id:"+ str(path))
                        # check if it reaches to wired gnB or not:
                        if self.traffic_list_temp[traffic].iab_node == len(self.iab_list):
                            # print("at t_ime step:",time_step,", via link:",path_id,", packet reac ti fiber gNB")
                            self.traffic_list_temp[traffic].stop_time = time_step
                            self.traffic_list_total.append(self.traffic_list_temp[traffic])
                            self.log("Hurraaaa, Traffic has reached to wired gnB, traffic id:" + str(
                                self.traffic_list_temp[traffic].t_id) + "with delay of:" + str(
                                self.traffic_list_temp[traffic].stop_time - self.traffic_list_temp[traffic].start_time))
                            # self.log("traffic index:"+str(traffic)+" has been removed from temp list of traffics")
                            # self.traffic_list_temp.pop(traffic)
                        else:
                            self.iab_list[self.traffic_list_temp[traffic].iab_node].equiped_buffer += \
                                self.traffic_list_temp[traffic].data_size
                            self.iab_list[self.traffic_list_temp[traffic].iab_node].total_pass_data += \
                                self.traffic_list_temp[traffic].data_size
                            # self.log(colored("updated:buffer size of cell:"+str(self.traffic_list_temp[traffic].iab_node)+",is:"+str(self.iab_list[ self.traffic_list_temp[traffic].iab_node].equiped_buffer), 'green', attrs=['bold']))
                            self.iab_list[self.traffic_list_temp[traffic].iab_node].bkh_req_list.insert(0,
                                                                                                        RequestDataType(
                                                                                                            data=
                                                                                                            self.traffic_list_temp[
                                                                                                                traffic].data_size,
                                                                                                            tr_id=t_id))
                    else:
                        self.log(colored("no more size", 'yellow', attrs=['bold']))
                        # print(colored("no more size", 'yellow', attrs=['bold']))
                        break
            # needs to receive
            elif cond_vector[cell] == 2:
                continue
            # cell is off in this transmission
            else:
                continue

    def drop_packet_per_node(self):
        drop_packet = np.zeros(self.num_cell)
        drop_packet_fr = np.zeros(self.num_cell)
        for cell in range(self.num_cell):
            drop_packet[cell] = len(self.iab_list[cell].bkh_sc_list) + len(self.iab_list[cell].bkh_req_list)
            drop_packet_fr[cell] = len(self.iab_list[cell].access_sc_list) + len(self.iab_list[cell].access_req_list)
        sorted_index = np.argsort(np.array(drop_packet))[::-1]
        sorted_index2 = np.argsort(np.array(drop_packet_fr))[::-1]

        print("Backhaul drop packet index per node is:", sorted_index)
        print("Backhaul drop packet per node is:", drop_packet[sorted_index])
        print("Fronthaul drop packet index per node is:", sorted_index2)
        print("Fronthaul drop packet per node is:", drop_packet_fr[sorted_index2])

    def run(self):
        for i in range(self.simulation_time_steps):
            if self.channel_update_ON:
                self.Bachkul_channel_update()

            # Pre Data processing
            Nk, Pk, Bk, achivable_rates_per_path_list = self.bakh_data_pre_process(i)

            #   step_by_step_visulaizer(self.num_cell, self.mode, Nk, Pk, Bk, achivable_rates_per_path_list)
            if self.scheduler == "mlr":
                path_id_s, cond_vector = self.bakh_scheduler(Pk, Nk, Bk, achivable_rates_per_path_list)
            else:
                raise ValueError("scheduler is not supported")

            self.bakh_step_two(i, path_id_s, cond_vector)

            # Fronthaul network
            self.fronthaul_network(i)

        self.drop_packet_per_node()
        sorted_index = np.argsort(self.generated_packet)[::-1]
        print("Generated packets indexs in each Cell:", sorted_index)
        print("Generated packets in each Cell:", self.generated_packet[sorted_index])
