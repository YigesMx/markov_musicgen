import os
import numpy as np
import pickle

from classes.song import Song
from utils.io import read_song
from utils.tools import chord_level, to_note_num

def read_songs():
    songs = []

    for file in os.listdir('data'):
        if file.endswith('.pkl'):
            song = read_song('data/' + file)
            songs.append(song)

    return songs


def do_statistics(songs: list[Song]):
    # 存储概率分布
    table_chord_loc = np.zeros([7, 16, 88])  # chord, loc => note
    table_chord_pre = np.zeros([7, 88, 88])  # chord, pre_note => note
    table_chord_pre_none_n1 = np.zeros([7, 88, 88])  # chord, pre_note(none_n1) => note
    table_chord_pre_next = np.zeros([7, 88, 88, 88])  # chord, pre_note, next_note => note
    table_chord_loc_pre_none_n1 = np.zeros([7, 16, 88, 88])  # chord, loc, pre_note(none_n1) => note

    for song in songs:
        pre_note_none_n1 = -1
        for i in range(len(song.tune)):
            chord = song.tune[i][0]
            crd_lv = chord_level[chord]
            for j in range(song.units_per_bar):

                cur_note = to_note_num(*(song.get_note_high(i, j)))
                # print(cur_note)
                # table_chord_loc
                table_chord_loc[crd_lv][j][cur_note] += 1

                # table_chord_pre
                loc = i * song.units_per_bar + j
                if loc > 0:
                    ii, jj = song.get_ij_loc(loc - 1)
                    pre_note = to_note_num(*song.get_note_high(ii, jj))
                    table_chord_pre[crd_lv][pre_note][cur_note] += 1

                    # table_chord_pre_next
                    if loc < song.get_total_len() - 1:
                        ii, jj = song.get_ij_loc(loc + 1)
                        next_note = to_note_num(*song.get_note_high(ii, jj))
                        table_chord_pre_next[crd_lv][pre_note][next_note][cur_note] += 1

                # table_chord_pre_none_n1
                # table_chord_loc_pre_none_n1
                if pre_note_none_n1 != -1:
                    table_chord_pre_none_n1[crd_lv][pre_note_none_n1][cur_note] += 1
                    table_chord_loc_pre_none_n1[crd_lv][j][pre_note_none_n1][cur_note] += 1

                if cur_note != 0:
                    # print(cur_note)
                    pre_note_none_n1 = cur_note

    return [table_chord_loc_pre_none_n1]


def learn():
    songs = read_songs()
    net = do_statistics(songs)

    # print(table_chord_pre[:, :, 33:48])
    file = open('net.pkl', 'wb')
    pickle.dump(net, file)
    file.close()


def load_net():
    file = open('net.pkl', 'rb')
    net = pickle.load(file)
    file.close()
    return net[0]
