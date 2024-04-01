import numpy as np

from classes.song import Song
from utils.tools import chord_level, to_note_high
from net import learn, load_net

# learn()
table_chord_loc_pre_none_n1, *_ = load_net()


def calc_prob(p: np.ndarray, prob_scale: float) -> tuple[bool, np.ndarray]:  # 计算概率
    p_sum = p.sum()
    if p_sum == 0:
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


def generate(song: Song(), pre_note: int, pre_note_none_n1: int, depth: int, prob_scale: float = 1.0,
             policy_mode: str = 'normal'):  # 尝试根据 pre_note 、位置、和弦 生成当前位置的音符并递归
    exist_policy = False
    policy = None

    i, j = song.get_ij_loc(depth)

    # select policy

    if pre_note != -1:  # 有前一个音符
        # exist_policy, policy = calc_prob(table_chord_loc_pre_none_n1[chord_level[song.tune[i][0]]][j][pre_note])
        exist_policy, policy = calc_prob(table_chord_loc_pre_none_n1[chord_level[song.tune[i][0]]][j][pre_note_none_n1],
                                         prob_scale)

    if pre_note == -1 or not exist_policy:  # 没有前一个音符，或者前一个音符的概率分布不存在
        #  将 policy 按 pre_note 方向相加
        table = table_chord_loc_pre_none_n1.sum(axis=2)
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

        if depth == song.get_total_len() - 1:
            return True

        # 递归
        new_pre_note_none_n1 = pre_note_none_n1 if note_num == 0 else note_num
        if generate(song=song, pre_note=int(note_num), pre_note_none_n1=new_pre_note_none_n1, depth=depth + 1,
                    prob_scale=prob_scale, policy_mode=policy_mode):
            return True
        else:
            policy[note_num] = 0
            exist_policy, policy = calc_prob(policy, prob_scale)
            if not exist_policy:
                return False

    return False


def musicgen(chord_list: list[str], name: str, bpm: int, unit_len: float, units_per_bar: int,
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

    if not generate(song=song, pre_note=-1, pre_note_none_n1=-1, depth=0, prob_scale=prob_scale,
                    policy_mode=policy_mode):
        assert "Failed to generate music"

    return song


if __name__ == '__main__':
    chord = ['C', 'Am', 'F', 'G', 'C', 'Am', 'F', 'G']
    # chord_list = ['C', 'C', 'Am', 'Am', 'F', 'F', 'G', 'G']
    # chord_list = ['C', 'C', 'Am', 'Am']
    song = musicgen(chord, "test", bpm=80, unit_len=1 / 16, units_per_bar=16, prob_scale=1.0, policy_mode='normal')

    print(song.tune)
    # song.save_wav()
    song.play()