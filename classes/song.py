from musicpy.musicpy import play
from musicpy.structures import track, chord

from utils.tools import level_name, chord_seq


class Song:
    def __init__(self):
        self.name = ""  # 歌名
        self.singer = ""  # 歌手
        self.style = ""  # 风格
        self.tune = []  # 只记录部分副歌

        self.bpm = 80
        self.key = ""
        self.unitLen = 1 / 16
        # 4/4拍
        self.unitsPerBar = 16

    def get_cho_loc(self, x):
        i = x // self.unitsPerBar
        j = x % self.unitsPerBar
        return i, j

    def get_note(self, i, j):
        return self.tune[i][1][j], self.tune[i][2][j]

    def get_total_len(self):
        return len(self.tune) * self.unitsPerBar

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

            i, j = self.get_cho_loc(loc)
            note, high = self.get_note(i, j)

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
                i, j = self.get_cho_loc(loc)
                if self.tune[i][1][j] == -1:
                    duration += 1
                    loc += 1
                else:
                    break

            print(" x " + str(duration))

            dur.append(duration * self.unitLen)
            itv.append(duration * self.unitLen)

        return mld, itv, dur, vol

    def crd_notes(self):
        # 生成和弦
        crd = []
        for line in self.tune:
            crd_notes = chord_seq[line[0]]
            for note in crd_notes:
                crd.append(note)
        return crd

    def play(self):  # 播放tune

        mld, itv, dur, vol = self.mld_notes()

        crd = self.crd_notes()

        # 播放
        play(track(
            content=chord(notes=mld, interval=itv, duration=dur, volume=vol) &
                    chord(notes=crd, interval=1 / 8, duration=1 / 8, volume=70),
            bpm=self.bpm,
            instrument=1,
        ),
            wait=True
        )  # 速度，乐器
