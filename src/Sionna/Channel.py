## import modules
import sionna
import numpy as np
import tensorflow as tf
from sionna.ofdm import ResourceGrid, ResourceGridMapper, LSChannelEstimator, LMMSEEqualizer
from sionna.mimo import StreamManagement
from sionna.mapping import Mapper, Demapper
from sionna.channel.tr38901 import UMi, PanelArray
from sionna.channel import gen_single_sector_topology as gen_topology
from sionna.channel import subcarrier_frequencies, cir_to_ofdm_channel
from sionna.channel import ApplyOFDMChannel, OFDMChannel
from sionna.signal import empirical_psd
from sionna.utils.metrics import compute_ber
from sionna.fec.ldpc.encoding import LDPC5GEncoder
from sionna.fec.ldpc.decoding import LDPC5GDecoder
from sionna.utils import ebnodb2no


def calculate_snr(received_power, noise_power):
    """
    Calculate SINR from the channel response and PSDs.
    
    Parameters:
    - channel_response: numpy array (frequency response of the channel)
    - signal_psd: numpy array (signal power spectral density)
    - noise_psd: numpy array (noise power spectral density)
    
    Returns:
    - SINR in db scale
    """
    # SINR calculation
    sinr = received_power / noise_power
    return 10 * np.log10(sinr)


def calculate_data_rate(bandwidth, sinr):
    """
    Calculate Shannon-based data rate.
    
    Parameters:
    - bandwidth: float (in Hz)
    - sinr: float (in linear scale)
    
    Returns:
    - Data rate in bits per second
    """
    # Shannon capacity formula
    data_rate = bandwidth * np.log2(1 + sinr)
    return data_rate / 1e6


class channel:
    def __init__(self, num_ut_ant=2, num_bs_ant=8, rng=42, subcarrier_spacing=15e3, fft_size=76, scenario="umi",
                 carrier_frequency=3.5e9,
                 direction="uplink", loc_tx=[1, 1, 1.5], loc_rx=[10, 12, 1.5], ebno_db=5, tx_power_dbm=30,
                 tx_ant_gain_db=8,
                 rx_ant_gain_db=5):
        # Define the number of UT and BS antennas.
        # a single UT and BS are supported.
        self.num_ut = 1
        self.num_bs = 1
        self.num_ut_ant = num_ut_ant
        self.num_bs_ant = num_bs_ant
        self.rngRun = rng
        self.scenario = scenario
        self.carrier_frequency = carrier_frequency
        self.direction = direction
        self.loc_tx = loc_tx
        self.loc_rx = loc_rx
        self.ebno_db = ebno_db
        self.tx_power_dbm = tx_power_dbm
        self.rx_ant_gain_db = rx_ant_gain_db
        self.tx_ant_gain_db = tx_ant_gain_db
        self.power_rx_effective = self.tx_power_dbm + self.rx_ant_gain_db + self.tx_ant_gain_db
        sionna.config.seed = self.rngRun
        tf.random.set_seed = self.rngRun
        np.random.seed = self.rngRun
        # The number of transmitted streams is equal to the number of UT antennas
        # in both uplink and downlink
        self.num_streams_per_tx = self.num_ut_ant

        self.rg = ResourceGrid(num_ofdm_symbols=14,
                               fft_size=fft_size,
                               subcarrier_spacing=subcarrier_spacing,
                               num_tx=1,
                               num_streams_per_tx=self.num_streams_per_tx,
                               cyclic_prefix_length=6,
                               num_guard_carriers=[5, 6],
                               dc_null=True,
                               pilot_pattern="kronecker",
                               pilot_ofdm_symbol_indices=[2, 11])
        self.bw = subcarrier_spacing * fft_size
        # Create an RX-TX association matrix
        # rx_tx_association[i,j]=1 means that receiver i gets at least one stream
        # from transmitter j. Depending on the transmission direction (uplink or downlink),
        # the role of UT and BS can change. However, as we have only a single
        # transmitter and receiver, this does not matter:
        rx_tx_association = np.array([[1]])

        # Instantiate a StreamManagement object
        # This determines which data streams are determined for which receiver.
        # In this simple setup, this is fairly easy. However, it can get more involved
        # for simulations with many transmitters and receivers.
        self.sm = StreamManagement(rx_tx_association, self.num_streams_per_tx)

    def set_seed(self, rngRun):
        sionna.config.seed = rngRun
        tf.random.set_seed = rngRun
        np.random.seed = rngRun

    def get_channel(self, ):
        bs_array = PanelArray(num_rows_per_panel=2,
                              num_cols_per_panel=int(self.num_bs_ant / 4),
                              polarization='dual',
                              polarization_type='cross',
                              antenna_pattern='38.901',
                              carrier_frequency=self.carrier_frequency)

        ut_array = PanelArray(num_rows_per_panel=1,
                              num_cols_per_panel=int(self.num_ut_ant / 2),
                              polarization='dual',
                              polarization_type='cross',
                              antenna_pattern='omni',
                              carrier_frequency=self.carrier_frequency)
        # Create channel model
        channel_model = UMi(carrier_frequency=self.carrier_frequency,
                            o2i_model='low',
                            ut_array=ut_array,
                            bs_array=bs_array,
                            direction="uplink",
                            enable_pathloss=True,
                            enable_shadow_fading=False)

        topology = gen_topology(1, 1, self.scenario)  # just for 1 sample
        # Set the topology
        ut_loc, bs_loc, ut_orientations, bs_orientations, ut_velocities, in_state = topology
        bs_loc = tf.constant(self.loc_tx, shape=(1, 1, 3), dtype=tf.float32)
        ut_loc = tf.constant(self.loc_rx, shape=(1, 1, 3), dtype=tf.float32)
        channel_model.set_topology(ut_loc,
                                   bs_loc,
                                   ut_orientations,
                                   bs_orientations,
                                   ut_velocities,
                                   in_state)
        _ = OFDMChannel(channel_model, self.rg, add_awgn=True, normalize_channel=False, return_channel=True)
        return channel_model

    def calc_channel_snr_data_rate(self, ):
        rg_mapper = ResourceGridMapper(self.rg)
        batch_size = 1  # Number of symbols we want to generate
        num_bits_per_symbol = 4  # 16-QAM has four bits per symbol
        coderate = 0.5  # Code rate
        n = int(self.rg.num_data_symbols * num_bits_per_symbol)  # Number of coded bits
        # print(rg.num_data_symbols)
        k = int(n * coderate)  # Number of information bits
        encoder = LDPC5GEncoder(k, n)
        binary_source = sionna.utils.BinarySource()
        b = binary_source([batch_size, 1, self.rg.num_streams_per_tx, encoder.k])
        mapper = Mapper("qam", num_bits_per_symbol)
        c = encoder(b)
        x = mapper(c)
        tx_power_linear = 10**(self.power_rx_effective / 10)  # Convert dBm to linear scale
        x_rg = tf.cast(tx_power_linear, tf.complex64) * rg_mapper(x)

        # The LS channel estimator will provide channel estimates and error variances
        ls_est = LSChannelEstimator(self.rg, interpolation_type="nn")
        # The LMMSE equalizer will provide soft symbols together with noise variance estimates
        lmmse_equ = LMMSEEqualizer(self.rg, self.sm)
        # The demapper produces LLR for all coded bits
        demapper = Demapper("app", "qam", num_bits_per_symbol)

        # The decoder provides hard-decisions on the information bits
        decoder = LDPC5GDecoder(encoder, hard_out=True)

        frequencies = subcarrier_frequencies(self.rg.fft_size, self.rg.subcarrier_spacing)

        no = ebnodb2no(self.ebno_db, num_bits_per_symbol, coderate, self.rg)

        channel  = self.get_channel()
        a, tau = channel(num_time_samples=self.rg.num_ofdm_symbols, sampling_frequency=1/self.rg.ofdm_symbol_duration)
        a = a 
        h_freq = cir_to_ofdm_channel(frequencies, a, tau, normalize=False)
        channel_freq = ApplyOFDMChannel(add_awgn=True)
        y = channel_freq([x_rg, h_freq, no])
        h_hat, err_var = ls_est ([y, no])
        x_hat, no_eff = lmmse_equ([y, h_hat, err_var, no])
        llr = demapper([x_hat, no_eff])
        b_hat = decoder(llr)
       # print("BER: {}".format(compute_ber(b, b_hat).numpy()))
        freq, psd=empirical_psd(y,show=False)
        snr = calculate_snr(np.mean(psd), no)
        data_rate = calculate_data_rate(40e6, snr)
        return snr, data_rate
