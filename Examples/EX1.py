from src.Main.SEBASI import Simulator
from src.Helper.KPIHelper import post_processing
import time


network_simulator = Simulator(simulation_time_steps=160, num_ue=100, mode="debug", source_rate=50000,
                               topology="smallMap", \
                               scheduler="mlr", packet_size=1000)

time_start = time.time()
network_simulator.run()
print("Total Simulation Run Time:", time.time() - time_start)
post_processing(network_simulator)