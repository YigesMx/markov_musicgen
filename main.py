import os
import time
import numpy as np
import pickle

from classes.song import Song
from utils.io import read_song
from utils.tools import chord_level, chord_seq, level_name, dig_level, to_note_num, to_note_high

# 存储概率分布
table_chord_loc = np.zeros([7, 16, 88])  # chord, loc => note
table_chord_pre = np.zeros([7, 88, 88])  # chord, pre_note => note
table_chord_pre_none_n1 = np.zeros([7, 88, 88])  # chord, pre_note(none_n1) => note
table_chord_pre_next = np.zeros([7, 88, 88, 88])  # chord, pre_note, next_note => note
table_chord_loc_pre_none_n1 = np.zeros([7, 16, 88, 88])  # chord, loc, pre_note(none_n1) => note


def read_songs():
    songs = []

    for file in os.listdir('data'):
        if file.endswith('.pkl'):
            song = read_song('data/' + file)
            songs.append(song)

    return songs


def do_statistics(songs: list[Song]):
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

    # print(table_chord_pre[:, :, 33:48])
    file = open('net.pkl', 'wb')
    pickle.dump([table_chord_loc_pre_none_n1], file)
    file.close()


def calc_prob(p: np.ndarray) -> tuple[bool, np.ndarray]:  # 计算概率
    p_sum = p.sum()
    if p_sum == 0:
        return False, p
    else:
        p = p / p_sum
        return True, p


MaxTriesPerLayer = 1000

def generate(song: Song(), pre_note: int, pre_note_none_n1: int, depth: int):  # 尝试根据 pre_note 、位置、和弦 生成当前位置的音符并递归
    exist_policy = False
    policy = None

    i, j = song.get_ij_loc(depth)

    # select policy

    if pre_note != -1:  # 有前一个音符
        # exist_policy, policy = calc_prob(table_chord_loc_pre_none_n1[chord_level[song.tune[i][0]]][j][pre_note])
        exist_policy, policy = calc_prob(table_chord_loc_pre_none_n1[chord_level[song.tune[i][0]]][j][pre_note_none_n1])

    if pre_note == -1 or not exist_policy:  # 没有前一个音符，或者前一个音符的概率分布不存在
        #  将 policy 按 pre_note 方向相加
        table = table_chord_loc_pre_none_n1.sum(axis=2)
        exist_policy, policy = calc_prob(table[chord_level[song.tune[i][0]]][j])

    if not exist_policy:
        return False

    # generate note
    for _ in range(MaxTriesPerLayer):
        # print(policy)

        # 随机选择当前位置的音符
        note_num = np.random.choice([int(i) for i in range(88)], size=1, p=policy)[0]
        while pre_note == -1 and note_num == 0:  # 如果是第一个音符，不允许是延时符
            note_num = np.random.choice([int(i) for i in range(88)], size=1, p=policy)[0]
            _ += 1
        note, high = to_note_high(note_num)
        song.tune[i][1][j] = note
        song.tune[i][2][j] = high

        if depth == song.get_total_len() - 1:
            return True

        # 递归
        new_pre_note_none_n1 = pre_note_none_n1 if note_num == 0 else note_num
        if generate(song=song, pre_note=int(note_num), pre_note_none_n1=new_pre_note_none_n1, depth=depth + 1):
            return True
        else:
            policy[note_num] = 0
            exist_policy, policy = calc_prob(policy)
            if not exist_policy:
                return False

    return False


def musicgen(name: str, bpm: int, unit_len: float, units_perBar: int, chord_list: list[str]):
    song = Song()
    song.name = name
    song.bpm = bpm
    song.unit_len = unit_len
    song.units_per_bar = units_perBar
    song.tune = [
        [
            chord_list[i],
            [0 for _ in range(units_perBar)],
            [0 for _ in range(units_perBar)]
        ]
        for i in range(len(chord_list))
    ]

    if not generate(song=song, pre_note=-1, pre_note_none_n1=-1, depth=0):
        assert "Failed to generate music"

    return song


if __name__ == '__main__':
    songs = read_songs()
    do_statistics(songs)

    chord_list = ['C', 'Am', 'F', 'G', 'C', 'Am', 'F', 'G']
    # chord_list = ['C', 'C', 'Am', 'Am', 'F', 'F', 'G', 'G']
    # chord_list = ['C', 'C', 'Am', 'Am']
    song = musicgen("test", 80, 1 / 16, 16, chord_list)

    print(song.tune)
    song.play()
