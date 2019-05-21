class Song:
    def __init__(self, song_id, title, artist, album, art, vote_count, duration):
        self.songID = song_id
        self.title = title
        self.artist = artist
        self.album = album
        self.albumArt = art
        self.voteCount = vote_count
        self.duration = duration

    # Waiting on API for play and pause
    # Also after thinking about it, the playback and pausing might be better handled
    # by the playlist, e.g. playlist.play(nextSong.songID), playlist.pause()
    def play(self):
        print("Play song '%s'" % self.title)

    def pause(self):
        print("Pause song '%s'" % self.title)

    def get_id(self):
        return self.songID

    def get_title(self):
        return self.title

    def upvote(self):
        self.voteCount += 1

    def downvote(self):
        self.voteCount -= 1

    # Overriding 'less than' comparison. Required for PQ
    # Flipped because python's heapq sorts by min to max
    def __lt__(self, other):
        return self.voteCount > other.voteCount
