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
    pickle.dump([table_chord_loc, table_chord_pre, table_chord_pre_next], file)
    file.close()


def calc_prob(p: np.ndarray) -> tuple[bool, np.ndarray]:  # 计算概率
    p_sum = p.sum()
    if p_sum == 0:
        return False, p
    else:
        p = p / p_sum
        return True, p


# class MarkovState:
#     def __init__(self):
#         self.tune = np.zeros((8, 16), dtype=int)
#         self.loc = 0
#         self.policy = None
#         self.note = 0
#         self.exist_policy = False


# def markov_search(state, i, j, pre, next):
#     note_list = [int(i) for i in range(88)]
#     crd_lv = chord_level[ChordList[i]]
#     if i == 0 and j == 0:
#         flag, prob = stat_prob(table_chord_loc[crd_lv][0])
#         if flag:
#             note_gen = np.random.choice(note_list, size=1, p=prob)
#         else:
#             note_gen = chord_seq[ChordList[i]][j]


# def markov_prob(s):
#     # calculate that p(next|now,next_chord)
#     chord_level = Chord_Level(ChordList[s.next_i])
#     tune = s.tune
#     note_now = tune[s.now_i][1][s.now_j] + tune[s.now_i][2][s.now_j] * 12 + 39
#     note_next = tune[s.next_i][1][s.next_j] + tune[s.next_i][2][s.next_j] * 12 + 39
#     return stat_prob(table_chord_pre[chord_level][note_now])


# def markov_initial(crd_lv):
#     # _, prob = stat_prob(table_chord_loc[crd_lv][0])
#     a = 39  # np.random.choice([int(i) for i in range(88)], size=1, p=prob)[0]
#     s_new = MarkovState()
#     s_new.loc = 0
#     s_new.note = a
#     s_new.tune = np.zeros((8, 16), dtype=int)
#     s_new.tune[0][0] = a
#     s_new.exist_policy, s_new.policy = calc_prob(table_chord_pre_none_n1[crd_lv][a])
#     return s_new
#
#
# def state_transfer(s, a, chord_list):
#     s_new = MarkovState()
#     pre_note = s.note
#     s_new.note = a
#     s_new.loc = s.loc + 2
#     if s_new.loc == 126:  # 只检查table_chord_pre_next
#         crd_lv = chord_level[chord_list[7]]
#         flag2, prob2 = calc_prob(table_chord_pre_next[crd_lv][pre_note][a])
#         if flag2:
#             s_new.tune = s.tune
#             s_new.tune[s_new.loc // 16][s_new.loc % 16] = a
#             pre_note = np.random.choice([int(i) for i in range(88)], size=1, p=prob2)[0]
#             s_new.tune[(s_new.loc - 1) // 16][(s_new.loc - 1) % 16] = pre_note
#             s_new.exist_policy = True
#         else:
#             s_new.exist_policy = False
#         return s
#     else:
#         crd_lv = chord_level[chord_list[s_new.loc // 16]]
#         flag1, prob1 = calc_prob(table_chord_pre_none_n1[crd_lv][a])
#         crd_lv = chord_level[chord_list[(s_new.loc - 1) // 16]]
#         flag2, prob2 = calc_prob(table_chord_pre_next[crd_lv][pre_note][a])
#         if flag1 and flag2:
#             s_new.policy = prob1
#             s_new.tune = s.tune
#             s_new.tune[s_new.loc // 16][s_new.loc % 16] = s.note
#             pre_note = np.random.choice([int(i) for i in range(88)], size=1, p=prob2)[0]
#             s_new.tune[(s_new.loc - 1) // 16][(s_new.loc - 1) % 16] = pre_note
#             s_new.exist_policy = True
#         else:
#             s_new.exist_policy = False
#         return s_new
#
#
# def markov_generate(chord_list):
#     # 初始化
#     s = [MarkovState() for i in range(128)]
#     initial_state = markov_initial(chord_level[chord_list[0]])
#     s[0] = initial_state
#     # print(s[0].policy)
#     t = 0
#     while t < 63:
#         if t < 0:
#             print('Warning! Bad initialization!')
#             return None
#         # print(s[0].policy)
#         if s[t].exist_policy:
#             # print(s[t].tune)
#             # print(t, s[t].loc)
#             prob = s[t].policy
#             a = np.random.choice([int(i) for i in range(88)], size=1, p=prob)[0]
#             next_s = state_transfer(s[t], a, chord_list)
#             t = t + 1
#             s[t] = next_s
#         else:
#             a = s[t].note
#             t = t - 1
#             prob = s[t].policy
#             # print(t, s[t].loc)
#             prob[a] = 0
#             s[t].exist_policy, s[t].policy = calc_prob(prob)
#
#     final_state = s[-1]
#     final_state.tune[7][15] = 26  # E和弦的最后一个音
#     return final_state
#
#
# def markov_song(chord_list, state):
#     # note_list = [int(i) for i in range(88)]
#     tune_length = len(chord_list)
#     tune_gen = [[] for _ in range(tune_length)]
#     for i in range(tune_length):
#         tune_gen[i] = (chord_list[i], [], [])
#         crd_lv = chord_level[chord_list[i]]
#         for j in range(16):
#             note_ij = state.tune[i][j]
#             note, high = to_note_high(note_ij)
#             tune_gen[i][1].append(dig_level[note] if note != -1 else -1)
#             tune_gen[i][2].append(high)
#     return tune_gen


# def regeneration(chord_list):
#     note_list = [int(i) for i in range(88)]
#     tune_lenth = len(chord_list)
#     tune_gen = [[] for i in range(tune_lenth)]
#     for i in range(tune_lenth):
#         tune_gen[i] = (chord_list[i], [], [])
#         crd_lv = chord_level[chord_list[i]]
#         for j in range(8):
#             flag, prob = stat_prob(table_chord_loc[crd_lv][j])
#             if flag:
#                 note_ij = np.random.choice(note_list, size=1, p=prob)
#             else:
#                 note_ij = chord_seq[chord_list[i]][j]
#             note_ij = note_ij[0]
#             tune_gen[i][1].append(dig_level[(note_ij - 39) % 12])
#             tune_gen[i][2].append((note_ij - 39) // 12)
#     return tune_gen

MaxTriesPerLayer = 10


def generate(song: Song(), pre_note: int, depth: int):  # 尝试根据 pre_note 、位置、和弦 生成当前位置的音符并递归
    exist_policy = False
    policy = None

    i, j = song.get_ij_loc(depth)

    if pre_note != -1:  # 有前一个音符
        exist_policy, policy = calc_prob(table_chord_loc_pre_none_n1[chord_level[song.tune[i][0]]][j][pre_note])

    if pre_note == -1 or not exist_policy:  # 没有前一个音符，或者前一个音符的概率分布不存在
        #  将 policy 按 pre_note 方向相加
        table = table_chord_loc_pre_none_n1.sum(axis=2)
        exist_policy, policy = calc_prob(table[chord_level[song.tune[i][0]]][j])

    if not exist_policy:
        return False

    # 随机选择当前位置的音符
    note_num = np.random.choice([int(i) for i in range(88)], size=1, p=policy)[0]
    while pre_note == -1 and note_num == 0:  # 如果是第一个音符，不允许是休止符
        note_num = np.random.choice([int(i) for i in range(88)], size=1, p=policy)[0]
    note, high = to_note_high(note_num)
    song.tune[i][1][j] = note
    song.tune[i][2][j] = high

    if depth == song.get_total_len() - 1:
        return True

    # 递归
    for _ in range(MaxTriesPerLayer):
        if generate(song, note, depth + 1):
            return True

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

    for _ in range(MaxTriesPerLayer):
        if generate(song, -1, 0):
            break
    else:
        assert False, "Failed to generate music"

    return song


if __name__ == '__main__':
    songs = read_songs()
    do_statistics(songs)

    chord_list = ['C', 'Am', 'F', 'G', 'C', 'Am', 'F', 'G']

    song = musicgen("test", 80, 1 / 16, 16, chord_list)

    # music = regeneration(ChordList)
    # s_markov = markov_generate(chord_list)
    # tune = markov_song(chord_list, s_markov)

    print(song.tune)
    song.play()
