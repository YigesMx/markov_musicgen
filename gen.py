import numpy as np

from classes.song import Song
from utils.tools import chord_level, to_note_high, to_note_num
from net import learn, load_net, sub_net

EPS = 1e-6

# learn()
# table_chord_loc_pre_none_n1, table_chord_loc_pre_next, *_ = load_net()
net = load_net()
table_chord_loc_pre_none_n1 = sub_net(net, ['chord', 'loc', 'pre_none_n1'])


def calc_prob(p: np.ndarray, prob_scale: float) -> tuple[bool, np.ndarray]:  # 计算概率
    p_sum = p.sum()
    if p_sum < EPS:
        return False, p
    else:
        p = p / p_sum
        p = p ** prob_scale
        p = p / p.sum()
        return True, p


def choose_from_policy(policy, policy_mode):
    if policy_mode == 'normal':
        return np.random.choice([int(i) for i in range(88)], size=1, p=policy)[0]
    elif policy_mode[:3] == 'max':
        # 例如为 max5 则从概率最大的5个音符中等概率选择
        max_num = int(policy_mode[3:])
        # 先选出最大的 max_num 个下标到 max_index
        max_index = np.argsort(policy)[-max_num:]
        # 如果对应 policy 为0，移除
        max_index = [i for i in max_index if policy[i] != 0]
        # 从 max_index 中等概率选择
        return np.random.choice(max_index, size=1)[0]
    elif policy_mode[:4] == 'pmax':
        # 例如为 max5 则从概率最大的5个音符中按规范化的子 policy 选择
        max_num = int(policy_mode[4:])
        # 先选出最大的 max_num 个下标到 max_index
        max_index = np.argsort(policy)[-max_num:]
        # 如果对应 policy 为0，移除
        max_index = [i for i in max_index if policy[i] != 0]
        # 生成新的 policy
        new_policy = policy[max_index]
        new_policy = new_policy / new_policy.sum()
        # 从 max_index 中等概率选择
        return np.random.choice(max_index, size=1, p=new_policy)[0]
    elif policy_mode == 'noneZero':
        # 从非零概率的音符中等概率选择
        non_zero_index = np.nonzero(policy)[0]
        return np.random.choice(non_zero_index, size=1)[0]
    elif policy_mode[:9] == 'threshold':
        # 从大于阈值的音符中等概率选择
        threshold = float(policy_mode[9:])
        threshold_index = np.nonzero(policy > threshold)[0]
        return np.random.choice(threshold_index, size=1)[0]


MaxTriesPerLayer = 1000


# def generate(song: Song(), pre_note: int, pre_note_none_n1: int, depth: int, prob_scale: float = 1.0,
#              policy_mode: str = 'normal'):  # 尝试根据 pre_note 、位置、和弦 生成当前位置的音符并递归
#     exist_policy = False
#     policy = None
#
#     i, j = song.get_ij_loc(depth)
#
#     # select policy
#
#     if pre_note != -1:  # 有前一个音符
#         # exist_policy, policy = calc_prob(table_chord_loc_pre_none_n1[chord_level[song.tune[i][0]]][j][pre_note])
#         exist_policy, policy = calc_prob(table_chord_loc_pre_none_n1[chord_level[song.tune[i][0]]][j][pre_note_none_n1],
#                                          prob_scale)
#
#     if pre_note == -1 or not exist_policy:  # 没有前一个音符，或者前一个音符的概率分布不存在
#         #  将 policy 按 pre_note 方向相加
#         # table = table_chord_loc_pre_none_n1.sum(axis=2)
#         table = sub_net(net, ['chord', 'loc'])
#         exist_policy, policy = calc_prob(table[chord_level[song.tune[i][0]]][j], prob_scale)
#
#     if not exist_policy:
#         return False
#
#     # generate note
#     for _ in range(MaxTriesPerLayer):
#         # print(policy)
#
#         # 随机选择当前位置的音符
#         note_num = choose_from_policy(policy, policy_mode)
#         while pre_note == -1 and note_num == 0:  # 如果是第一个音符，不允许是延时符
#             note_num = choose_from_policy(policy, policy_mode)
#             _ += 1
#         note, high = to_note_high(note_num)
#         song.tune[i][1][j] = note
#         song.tune[i][2][j] = high
#
#         if depth == song.get_total_len() - 1:
#             return True
#
#         # 递归
#         new_pre_note_none_n1 = pre_note_none_n1 if note_num == 0 else note_num
#         if generate(song=song, pre_note=int(note_num), pre_note_none_n1=new_pre_note_none_n1, depth=depth + 1,
#                     prob_scale=prob_scale, policy_mode=policy_mode):
#             return True
#         else:
#             policy[note_num] = 0
#             exist_policy, policy = calc_prob(policy, prob_scale)
#             if not exist_policy:
#                 return False
#
#     return False


def generate_ni(song: Song(), base_table: list, pre_note: int, pre_note_none_n1: int, depth: int, step: int,
                prob_scale: float = 1.0,
                policy_mode: str = 'normal'):
    exist_policy = False
    policy = None

    i, j = song.get_ij_loc(depth)

    # select policy

    if pre_note != -1:  # 有前一个音符
        exist_policy, policy = calc_prob(base_table[chord_level[song.tune[i][0]]][j][pre_note_none_n1],
                                         prob_scale)

    if pre_note == -1 or not exist_policy:  # 没有前一个音符，或者前一个音符的概率分布不存在
        #  将 policy 按 pre_note 方向相加
        table = sub_net(net, ['chord', 'loc'])
        exist_policy, policy = calc_prob(table[chord_level[song.tune[i][0]]][j], prob_scale)

    if not exist_policy:
        return False

    # generate note
    for _ in range(MaxTriesPerLayer):
        # print(policy)

        # 随机选择当前位置的音符
        note_num = choose_from_policy(policy, policy_mode)
        while pre_note == -1 and note_num == 0:  # 如果是第一个音符，不允许是延时符
            note_num = choose_from_policy(policy, policy_mode)
            _ += 1
        note, high = to_note_high(note_num)
        song.tune[i][1][j] = note
        song.tune[i][2][j] = high

        if depth >= song.get_total_len() - step:
            return True

        # 递归
        new_pre_note_none_n1 = pre_note_none_n1 if note_num == 0 else note_num
        if generate_ni(song=song, base_table=base_table, pre_note=int(note_num), pre_note_none_n1=new_pre_note_none_n1,
                       depth=depth + step, step=step, prob_scale=prob_scale, policy_mode=policy_mode):
            return True
        else:
            policy[note_num] = 0
            exist_policy, policy = calc_prob(policy, prob_scale)
            if not exist_policy:
                return False

    return False


def generate_pre_next(song: Song(), base_table: list, depth: int, step: int,
                 prob_scale: float = 1.0,
                 policy_mode: str = 'normal'):
    exist_policy = False
    policy = None

    i, j = song.get_ij_loc(depth)

    # select policy
    pre_i, pre_j = song.get_ij_loc(depth - 1)
    pre_note = to_note_num(*(song.get_note_high(pre_i, pre_j)))
    next_i, next_j = song.get_ij_loc(depth + 1)
    next_note = to_note_num(*(song.get_note_high(next_i, next_j)))

    if next_note is not None:
        exist_policy, policy = calc_prob(base_table[chord_level[song.tune[i][0]]][pre_note][next_note],
                                         prob_scale)
    else:
        # 将 policy 按 next_note 方向相加
        table = sub_net(net, ['chord', 'pre'])
        exist_policy, policy = calc_prob(table[chord_level[song.tune[i][0]]][pre_note], prob_scale)

    if not exist_policy:
        return False

    # generate note
    for _ in range(MaxTriesPerLayer):
        # print(policy)

        # 随机选择当前位置的音符
        note_num = choose_from_policy(policy, policy_mode)
        while (note_num == 39 and next_note == 0) or (pre_note == 39 and note_num == 0):
            # 如果后一个音符是延时符，不允许是空拍；如果前一个音符是空拍，不允许是延时符
            note_num = choose_from_policy(policy, policy_mode)
            _ += 1
            if _ >= MaxTriesPerLayer:
                return False
        if pre_note == 39 and note_num == 0:
            assert False, "pre_note == 39 and note_num == 0"
        elif next_note == 0 and note_num == 39:
            assert False, "next_note == 0 and note_num == 39"

        note, high = to_note_high(note_num)
        song.tune[i][1][j] = note
        song.tune[i][2][j] = high

        if depth >= song.get_total_len() - step:
            return True

        # 递归
        if generate_pre_next(song=song, base_table=base_table, depth=depth + step, step=step,
                             prob_scale=prob_scale, policy_mode=policy_mode):
            return True
        else:
            policy[note_num] = 0
            exist_policy, policy = calc_prob(policy, prob_scale)
            if not exist_policy:
                return False

    return False


def generate_with_rule(song: Song(), rule: list, prob_scale: float = 1.0, policy_mode: str = 'normal'):
    step = len(rule)
    for start, rule_line in enumerate(rule):
        if 'next' not in rule_line:
            if not generate_ni(song=song, base_table=sub_net(net, rule_line), pre_note=-1, pre_note_none_n1=-1,
                               depth=start, step=step, prob_scale=prob_scale, policy_mode=policy_mode):
                return False
        else:
            if not generate_pre_next(song=song, base_table=sub_net(net, rule_line), depth=start, step=step,
                                     prob_scale=prob_scale, policy_mode=policy_mode):
                return False
    return True


def musicgen(chord_list: list[str], rule: list, name: str, bpm: int, unit_len: float, units_per_bar: int,
             prob_scale: float = 1.0, policy_mode: str = 'normal') -> Song:
    song = Song(name=name, bpm=bpm, unit_len=unit_len, units_per_bar=units_per_bar)
    song.tune = [
        [
            chord_list[i],
            [0 for _ in range(units_per_bar)],
            [0 for _ in range(units_per_bar)]
        ]
        for i in range(len(chord_list))
    ]

    if not generate_with_rule(song=song, rule=rule, prob_scale=prob_scale, policy_mode=policy_mode): \
            assert "Failed to generate music"

    # if not generate(song=song, pre_note=-1, pre_note_none_n1=-1, depth=0, prob_scale=prob_scale,
    #                 policy_mode=policy_mode):
    #     assert "Failed to generate music"

    return song


if __name__ == '__main__':
    chord = ['C', 'Am', 'F', 'G', 'C', 'Am', 'F', 'G']
    # chord = ['C', 'C', 'Am', 'Am', 'F', 'F', 'G', 'G']
    # chord = ['C', 'C', 'Am', 'Am']
    r1 = [
        ['chord', 'loc', 'pre_none_n1'],
    ]
    r2 = [
        ['chord', 'loc', 'pre_none_n1'],
        ['chord', 'pre', 'next']
    ]
    new_song = musicgen(chord_list=chord, rule=r2, name="test", bpm=80, unit_len=1 / 16, units_per_bar=16,
                        prob_scale=1.0,
                        policy_mode='normal')

    print(new_song.tune)
    # song.save_wav()
    new_song.play()
