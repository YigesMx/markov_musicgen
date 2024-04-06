level_name = {1: 'C', 2: 'D', 3: 'E', 4: 'F', 5: 'G', 6: 'A',
              7: 'B'}  # , 12: 'C#', 23: 'D#', 45: 'F#', 56: 'G#', 67: 'A#'}  # 级数音名

# chord_seq = {
#     'C': ['C3', 'E3', 'G3', 'C4', 'E4', 'C4', 'G3', 'E3'],
#     'D': ['D2', 'F#2', 'A2', 'D3', 'F#3', 'D3', 'A2', 'F#2'],
#     'Dm': ['D2', 'F2', 'A2', 'D3', 'F3', 'D3', 'A2', 'F2'],
#     'E': ['E2', 'G#2', 'B2', 'E3', 'G#3', 'E3', 'B2', 'G#2'],
#     'Em': ['E2', 'G2', 'B2', 'E3', 'G3', 'E3', 'B2', 'G2'],
#     'Am': ['A2', 'C3', 'E3', 'A3', 'C4', 'A3', 'E3', 'C3'],
#     'F': ['F2', 'A2', 'C3', 'F3', 'A3', 'F3', 'C3', 'A2'],
#     'Fm': ['F2', 'Ab2', 'C3', 'F3', 'Ab3', 'F3', 'C3', 'Ab2'],
#     'G': ['G2', 'B2', 'D2', 'G3', 'B3', 'G3', 'D2', 'B2'],
# }


chord_seq = {
    'C': ['C3', 'G3', 'C4', 'G3', 'E4', 'G3', 'C4', 'G3'],
    'D': ['D2', 'A2', 'D3', 'A2', 'F#3', 'A2', 'D3', 'A2'],
    'Dm': ['D2', 'A2', 'D2', 'A2', 'F3', 'A2', 'D3', 'A2'],
    'E': ['E2', 'B2', 'E3', 'B2', 'G#3', 'B2', 'E3', 'B2'],
    'Em': ['E2', 'B2', 'E3', 'B2', 'G3', 'B2', 'E3', 'B2'],
    'Am': ['A2', 'E3', 'A3', 'E3', 'C4', 'E3', 'A3', 'E3'],
    'F': ['F2', 'C3', 'F3', 'C3', 'A3', 'C3', 'F3', 'C3'],
    'Fm': ['F2', 'C3', 'F3', 'C3', 'Ab3', 'C3', 'F3', 'C3'],
    'G': ['G2', 'D3', 'G3', 'D3', 'B3', 'D3', 'G3', 'D3'],
}

chord_level = {'C': 1, 'Cm': 1, 'D': 2, 'Dm': 2, 'E': 3, 'Em': 3, 'F': 4,
               'Fm': 4, 'G': 5, 'Gm': 5, 'A': 6, 'Am': 6, 'B': 7, 'Bm': 7}  # 和弦级数

dig_level = {0: 1, 1: 12, 2: 2, 3: 23, 4: 3, 5: 4,
             6: 45, 7: 5, 8: 56, 9: 6, 10: 67, 11: 7}  # 数字级数化


# def to_note_num(note, high):
#     if note == -1:
#         return 0
#     else:
#         return 12 * high + note + 39

def to_note_num(note, high):
    if note is None:
        return None
    elif note == -1:
        return 0
    elif note == 0:
        return 39
    else:
        note_num = note + 8 * high + 39
        assert 0 <= note_num <= 87
        return note_num


# def to_note_high(num):
#     if num == 0:
#         return -1, 0
#     else:
#         return ((num - 39) % 12 + 12) % 12, (num - 39) // 12

def to_note_high(num):
    if num == 0:
        return -1, 0
    elif num == 39:
        return 0, 0
    else:
        note, high = ((num - 39) % 8 + 8) % 8, (num - 39) // 8
        assert -1 <= note <= 7 and -3 <= high <= 3, f'{note}, {high}'
        return note, high
