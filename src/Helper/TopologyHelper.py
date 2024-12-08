import numpy as np


def topology_gen(topology, bs_height):
    '''
    generate topology for simulation
    :return:
    '''
    if topology == "Padova":
        gnb_loc = np.array((2500, 1250, bs_height))
        iab_nodes_loc_list_tim = np.array(((240, 456, bs_height), (230, 720, bs_height), (280, 1450, bs_height),
                                           (660, 490, bs_height), (650, 1800, bs_height), (710, 1200, bs_height),
                                           (830, 240, bs_height), (820, 820, bs_height), (840, 1100, bs_height),
                                           (860, 1250, bs_height), (970, 200, bs_height), (960, 1010, bs_height),
                                           (970, 1310, bs_height), (1080, 1440, bs_height), (1100, 400, bs_height),
                                           (1200, 410, bs_height), (1240, 580, bs_height), (1220, 610, bs_height),
                                           (1250, 1030, bs_height), (1300, 1200, bs_height), (1200, 1450, bs_height),
                                           (1250, 1670, bs_height), (1200, 1880, bs_height), (1050, 2150, bs_height),
                                           (1500, 20, bs_height), (1780, 240, bs_height), (1680, 1050, bs_height),
                                           (1800, 960, bs_height), (1650, 1800, bs_height), (1550, 2001, bs_height),
                                           (1920, 1200, bs_height), (2040, 1560, bs_height), (2160, 600, bs_height),
                                           (2250, 1010, bs_height), (2150, 1300, bs_height), (2150, 1800, bs_height),
                                           (2280, 2040, bs_height)))

        iab_nodes_loc_list_vodafone = np.array(((179, 700, bs_height), (240, 1010, bs_height), (250, 1500, bs_height),
                                                (350, 2040, bs_height), (610, 480, bs_height), (600, 960, bs_height),
                                                (720, 1200, bs_height), (700, 1400, bs_height), (840, 850, bs_height),
                                                (960, 1000, bs_height), (900, 960, bs_height), (970, 950, bs_height),
                                                (1200, 1440, bs_height), (1350, 130, bs_height),
                                                (1340, 1000, bs_height), (1250, 2000, bs_height),
                                                (1290, 2030, bs_height), (1540, 20, bs_height), (1440, 600, bs_height),
                                                (1600, 1204, bs_height), (1590, 2010, bs_height),
                                                (1800, 240, bs_height), (1770, 720, bs_height), (1820, 900, bs_height),
                                                (1700, 1680, bs_height), (1960, 1200, bs_height),
                                                (2160, 600, bs_height), (2000, 1480, bs_height),
                                                (2160, 1800, bs_height), (2220, 140, bs_height), (2250, 960, bs_height),
                                                (2300, 2000, bs_height),))

        iab_nodes_loc_list_windthree = np.array(((240, 360, bs_height), (200, 720, bs_height), (235, 1002, bs_height),
                                                 (267, 1450, bs_height), (400, 2100, bs_height), (610, 480, bs_height),
                                                 (620, 880, bs_height), (600, 1020, bs_height), (680, 1500, bs_height),
                                                 (700, 1800, bs_height), (720, 1300, bs_height), (840, 840, bs_height),
                                                 (1000, 300, bs_height), (1000, 970, bs_height),
                                                 (1039, 1000, bs_height), (960, 960, bs_height),
                                                 (1220, 1400, bs_height), (1240, 480, bs_height),
                                                 (1390, 720, bs_height), (1340, 700, bs_height),
                                                 (1290, 1000, bs_height), (1150, 2000, bs_height),
                                                 (1500, 20, bs_height), (1400, 1400, bs_height), (1600, 730, bs_height),
                                                 (1700, 920, bs_height), (1720, 1000, bs_height),
                                                 (2150, 340, bs_height), (2040, 600, bs_height),
                                                 (1980, 1450, bs_height), (2160, 1900, bs_height)))
        iab_nodes_loc_list = np.concatenate(
            (iab_nodes_loc_list_tim, iab_nodes_loc_list_vodafone, iab_nodes_loc_list_windthree))

    elif topology == "smallMap":
        gnb_loc = np.array((200, 200, bs_height))
        iab_nodes_loc_list = np.array(((270, 239, bs_height), (200, 160, bs_height), (180, 270, bs_height),
                                       (230, 290, bs_height), (240, 100, bs_height),
                                       (320, 175, bs_height), (100, 210, bs_height), (165, 55, bs_height),
                                       (145, 330, bs_height), (85, 25, bs_height),
                                       (245, 180, bs_height), (380, 190, bs_height), (305, 240, bs_height),
                                       (40, 20, bs_height), (140, 170, bs_height),
                                       (300, 75, bs_height), (100, 73, bs_height), (204, 96, bs_height),
                                       (89, 140, bs_height), (10, 350, bs_height),
                                       (30, 290, bs_height), (104, 270, bs_height), (44, 220, bs_height)))

    else:
        gnb_loc = np.array((220, 75, 15))
        iab_nodes_loc_list = np.array(((170, 30, 15), (170, 90, 15), (180, 70, 15), (190, 100, 15), (140, 20, 15),
                                       (120, 5, 15), (125, 65, 15), (125, 95, 15), (145, 130, 15), (85, 25, 15),
                                       (85, 80, 15), (80, 110, 15), (105, 140, 15), (40, 20, 15), (55, 45, 15),
                                       (10, 73, 15), (34, 96, 15), (50, 140, 15)))

    return gnb_loc, iab_nodes_loc_list
