import heapq
from song import Song

class Playlist:
    def __init__(self):
        self.songPQ = []
        self.code = ''

    def setCode(self, code):
        self.code = code

    def getCode(self):
        return self.code

    def addSong(self, song):
        #print(-song.voteCount)
        heapq.heappush(self.songPQ, (-song.voteCount, song)) # push the negative value to have a max-heap

    def addSongs(self, songs):
        for song in songs:
            self.addSong(song)

    def deleteSong(self, song):
        for i, s in enumerate(self.songPQ):
            if s is song:
                # replace song to delete with last song in PQ
                self.songPQ[i] = self.songPQ[-1]
                self.songPQ.pop()                   # pop, removing last song in PQ
                self.refreshPlaylist()              # re-heap

    def refreshPlaylist(self):
        heapq.heapify(self.songPQ)

    def getNextSong(self):
        self.refreshPlaylist()
        if len(self.songPQ) > 0:    # check if pq empty
            nextSong = heapq.heappop(self.songPQ)
        else:
            nextSong = None
        return nextSong