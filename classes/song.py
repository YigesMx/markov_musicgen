from musicpy.musicpy import play
# from musicpy.daw import daw
from musicpy.structures import track, chord

from utils.tools import level_name, chord_seq


class Song:
    def __init__(self, name="", singer="", style="", bpm=80, key="", unit_len=1 / 16, units_per_bar=16):
        self.name = name  # 歌名
        self.singer = singer  # 歌手
        self.style = style  # 风格
        self.tune = []  # 曲谱

        self.bpm = bpm  # 每分钟节拍数
        self.key = key  # 调性
        self.unit_len = unit_len  # 单位时长
        # 4/4拍
        self.units_per_bar = units_per_bar  # 每小节的单位数

    def get_ij_loc(self, x):
        i = x // self.units_per_bar
        j = x % self.units_per_bar
        return i, j

    def get_note_high(self, i, j):
        return self.tune[i][1][j], self.tune[i][2][j]

    def get_total_len(self):
        return len(self.tune) * self.units_per_bar

    def mld_notes(self):
        default = 5  # 默认音高
        # https://wenku.baidu.com/view/ed23999bd5bbfd0a78567338.html 乐器对照表

        # 生成旋律
        total_len = self.get_total_len()

        mld = []
        itv = []
        dur = []
        vol = []

        loc = 0
        while loc < total_len:

            i, j = self.get_ij_loc(loc)
            note, high = self.get_note_high(i, j)

            print(note, end='')

            if note == 0:
                mld.append('C0')
                vol.append(0)
            else:
                mld.append(level_name[note] + str(default + high))
                vol.append(100)

            loc += 1

            duration = 1
            while loc < total_len:
                i, j = self.get_ij_loc(loc)
                if self.tune[i][1][j] == -1:
                    duration += 1
                    loc += 1
                else:
                    break

            print(" x " + str(duration))

            dur.append(duration * self.unit_len)
            itv.append(duration * self.unit_len)

        return mld, itv, dur, vol

    def crd_notes(self):
        # 生成和弦
        crd = []
        for line in self.tune:
            crd_notes = chord_seq[line[0]]
            for note in crd_notes:
                crd.append(note)
        return crd

    def get_trk(self):
        mld, itv, dur, vol = self.mld_notes()

        crd = self.crd_notes()

        trk = track(
            content=chord(notes=mld, interval=itv, duration=dur, volume=vol) &
                    chord(notes=crd, interval=1 / 8, duration=1 / 8, volume=70),
            bpm=self.bpm,
            instrument=1,
        )

        return trk

    def save_wav(self):
        trk = self.get_trk()

        # new_daw = daw(num=1, name='export')
        # new_daw.play(trk)
        # new_daw.export(trk, "export", "wav")

    def play(self):  # 播放tune

        trk = self.get_trk()
        # 播放
        play(trk, wait=True)


