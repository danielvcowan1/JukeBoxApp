schema_users = """
CREATE TABLE IF NOT EXISTS tblUsers (
	IDUser INTEGER PRIMARY KEY AUTOINCREMENT,
	DisplayName TEXT NOT NULL,
	LastLoginDate DATE NOT NULL,
	AccessToken TEXT UNIQUE,
	SpotifyUserId TEXT NOT NULL UNIQUE
);
"""
schema_playlists = """
CREATE TABLE IF NOT EXISTS tblPlaylists (
	IDPlaylist INTEGER PRIMARY KEY AUTOINCREMENT,
	Name TEXT NOT NULL,
	Description TEXT,
	DateCreated Date NOT NULL,
	AccessCode TEXT NOT NULL UNIQUE,
	Public INTEGER NOT NULL,
	IDUser INTEGER NOT NULL,
	FOREIGN KEY(IDUser) REFERENCES tblUsers(IDUser)
);
"""
schema_songs = """
CREATE TABLE IF NOT EXISTS tblSongs (
	IDSong INTEGER PRIMARY KEY AUTOINCREMENT,
	Name TEXT NOT NULL,
	Artist TEXT NOT NULL,
	Album TEXT NOT NULL,
	SpotifySongID TEXT NOT NULL,
	IDPlaylist INTEGER NOT NULL,
	Duration INTEGER NOT NULL,
	UNIQUE(SpotifySongID, IDPlaylist),
	FOREIGN KEY(IDPlaylist) REFERENCES tblPlaylists(IDPlaylist)
);
"""
schema_song_votes = """CREATE TABLE IF NOT EXISTS tblSongVotes (
	IDPlaylist INTEGER,
	IDSong INTEGER,
	VoteValue INTEGER NOT NULL,
	IDUserVote INTEGER NOT NULL,
	FOREIGN KEY(IDUserVote) REFERENCES tblUsers(IDUser),
	FOREIGN KEY(IDPlaylist) REFERENCES tblPlaylists(IDPlaylist),
	FOREIGN KEY(IDSong) REFERENCES tblSongs(IDSong)
);
"""
