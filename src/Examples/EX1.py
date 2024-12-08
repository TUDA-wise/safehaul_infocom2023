
import time
import sys
print(sys.path)
from src.Main.SEBASI import Simulator
from src.Helper.KPIHelper import post_processing
network_simulator = Simulator(simulation_time_steps=160, num_ue=100, mode="run", source_rate=50,
                               topology="smallMap", \
                               scheduler="mlr", packet_size=1, channel_update_ON=False)

time_start = time.time()
network_simulator.run()
print("Total Simulation Run Time:", time.time() - time_start)
post_processing(network_simulator)