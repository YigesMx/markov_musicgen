import pickle
import os

from classes.song import Song


# save Song
def save_song(song: Song):
    file = open(song.name + '.pkl', 'wb')
    pickle.dump(song, file)
    file.close()


# read Song
def read_song(_dir) -> Song:
    file = open(_dir, 'rb')
    song = pickle.load(file)
    file.close()
    return song
