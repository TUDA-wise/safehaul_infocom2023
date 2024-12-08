import numpy as np
import tensorflow as tf
from sionna.channel import ApplyOFDMChannel
from sionna.signal import empirical_psd


def read_codebook(code_book_filename):
    codebook = open(code_book_filename, 'r')

    # to pass init lines of CodeBook
    for i in range(6):
        temp_line = codebook.readline()
    codebook_size = int(codebook.readline())
    ant_size = int(codebook.readline())

    complex_bf = np.zeros((codebook_size, ant_size), dtype=complex)
    # print(complex_bf.shape)
    cnt = 0
    for line in codebook:

        temp_list = line.split(";")
        for i in range(len(temp_list)):
            temp_list[i] = temp_list[i].replace("(", "")
            temp_list[i] = temp_list[i].replace(")", "")
            data = temp_list[i].split(",")
            complex_bf[cnt][i] = (complex(float(data[0]), float(data[1])))
        cnt += 1
    complex_bf_tf = tf.convert_to_tensor(complex_bf, dtype=tf.complex64)
    return complex_bf_tf


def beam_forming(x_rg, bf_codebook, h_freq, no, test=False):
    channel_freq = ApplyOFDMChannel(add_awgn=True)
    psd_max = 0
    if test:
        bf_sample = tf.constant([0.849664 + 0.012961j, 0.856872 + 0.243445j, -0.21808 + 0.822233j, 0.249664 + 0.012961j,
                                 0.056872 + 0.943445j, -0.21808 + 0.122233j, 0.949664 + 0.012961j,
                                 0.056872 + 0.243445j], shape=[8], dtype=tf.complex64)

        x_rg_bf = np.zeros(shape=tf.shape(x_rg), dtype=np.complex64)
        for i in range(len(x_rg[:, ])):
            for j in range(len(x_rg[0, :])):
                for k in range(len(x_rg[0, 0, 0, :])):
                    for m in range(len(x_rg[0, 0, 0, 0, :])):
                        x_rg_bf[i, j, :, k, m] = tf.math.multiply(bf_sample, x_rg[i, j, :, k, m])

        x_rg_bf_tf = tf.convert_to_tensor(x_rg_bf, dtype=tf.complex64)
        return x_rg_bf_tf
    else:
        for bf_i in range(len(bf_codebook)):
            x_rg_bf = np.zeros(shape=tf.shape(x_rg), dtype=np.complex64)
            for i in range(len(x_rg[:, ])):
                for j in range(len(x_rg[0, :])):
                    for k in range(len(x_rg[0, 0, 0, :])):
                        for m in range(len(x_rg[0, 0, 0, 0, :])):
                            x_rg_bf[i, j, :, k, m] = tf.math.multiply(bf_codebook[bf_i], x_rg[i, j, :, k, m])

            x_rg_bf_tf = tf.convert_to_tensor(x_rg_bf, dtype=tf.complex64)
            y = channel_freq([x_rg_bf_tf, h_freq, no])
            freq, psd = empirical_psd(y, show=False)
            # print(np.mean(psd))
            if np.mean(psd) > psd_max:
                bf = bf_codebook[bf_i]
                x_bf = x_rg_bf_tf
                psd_max = np.mean(psd)

        return bf, x_bf


def beam_forming_h(x_rg, bf_codebook, h_freq, no, test=False):
    channel_freq = ApplyOFDMChannel(add_awgn=True)
    psd_max = 0
    if test:
        bf_sample = tf.constant([0.849664 + 0.012961j, 0.856872 + 0.243445j, -0.21808 + 0.822233j, 0.249664 + 0.012961j,
                                 0.056872 + 0.943445j, -0.21808 + 0.122233j, 0.949664 + 0.012961j,
                                 0.056872 + 0.243445j], shape=[8], dtype=tf.complex64)

        x_rg_bf = np.zeros(shape=tf.shape(x_rg), dtype=np.complex64)
        for i in range(len(x_rg[:, ])):
            for j in range(len(x_rg[0, :])):
                for k in range(len(x_rg[0, 0, 0, :])):
                    for m in range(len(x_rg[0, 0, 0, 0, :])):
                        x_rg_bf[i, j, :, k, m] = tf.math.multiply(bf_sample, x_rg[i, j, :, k, m])

        x_rg_bf_tf = tf.convert_to_tensor(x_rg_bf, dtype=tf.complex64)
        return x_rg_bf_tf
    else:
        for bf_i in range(len(bf_codebook)):
            h_freq_bf = np.zeros(shape=tf.shape(h_freq), dtype=np.complex64)
            for i in range(len(h_freq[:, ])):
                for j in range(len(h_freq[0, :])):
                    for i2 in range(len(h_freq[0, 0, :])):
                        for j2 in range(len(h_freq[0, 0, 0, :])):
                            for k in range(len(h_freq[0, 0, 0, 0, 0, :])):
                                for m in range(len(h_freq[0, 0, 0, 0, 0, 0, :])):
                                    h_freq_bf[i, j, i2, j2, :, k, m] = tf.math.multiply(bf_codebook[bf_i],
                                                                                        h_freq[i, j, i2, j2, :, k, m])

            x_rg_bf_tf = tf.convert_to_tensor(h_freq_bf, dtype=tf.complex64)
            y = channel_freq([x_rg, x_rg_bf_tf, no])
            freq, psd = empirical_psd(y, show=False)
            # print(np.mean(psd))
            if np.mean(psd) > psd_max:
                bf = bf_codebook[bf_i]
                x_bf = x_rg_bf_tf
                psd_max = np.mean(psd)

        # print(np.mean(psd_max))
        return bf, x_bf
