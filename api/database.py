import sqlite3
from sqlite3 import (
    Error,
    IntegrityError,
    OperationalError
)
from contextlib import contextmanager
from jukebox_schema import (
    schema_users,
    schema_playlists,
    schema_songs,
    schema_song_votes
)
import os


class Database:

    def __init__(self, db_path):
        self.path = db_path
        db_exists = os.path.isfile(db_path)
        self.cnxn = sqlite3.connect(self.path)
        if not db_exists:
            print('initializing Jukebox database...')
            self.initialize()


    def execute(self, sql, params=[]):
        """Executes an SQL statment on the connected database.
        SQL statements can be parameterized by adding '?' in the string and
        then including the parameter in the params keyword argument
        
        E.G.:
        sql = "SELECT * FROM tblUsers where IDUser = ?"
        user_id = 7
        db.execute(sql, params=[user_id])

        Arguments
        @param sql: sql statement to be executed
        @param params: list of parameters to inject into sql statement
        
        @returns: list of tuples containing table data; returns None if error
        occurs; returns empty list for update/modify statments
        """
        with self.cnxn:
            try:
                #Executes SQL and returns cursor
                cursor = self.cnxn.execute(sql, params)
                #Fetch all table data from cursor
                data = cursor.fetchall()
                return data
            except sqlite3.Error as e:
                print('Database Error:', e)
                return 

    def initialize(self):
        """Initializes Jukebox schema as defined in 'jukebox_schema.py' """
        self.execute(schema_users)
        self.execute(schema_playlists)
        self.execute(schema_songs)
        self.execute(schema_song_votes)

    def get_user(self, spotify_id):
        qry_user = """SELECT * FROM tblUsers WHERE SpotifyUserId = ?"""
        user = self.execute(qry_user, params=[spotify_id])
        if user:
            return user[0]
        return

    def get_user_id(self, spotify_id):
        qry_user = """SELECT * FROM tblUsers WHERE SpotifyUserId = ?"""
        user = self.execute(qry_user, params=[spotify_id])
        if user:
            return user[0][0]
        return

    # Specify vote_value = 1 for upvote, vote_value = -1 for downvote
    def vote_song(self, user_id, song_id, playlist_id, vote_value):
        try:
            cursor = self.cnxn.cursor()
            song_vote = """INSERT INTO tblSongVotes(
                             IDPlaylist, IDSong, VoteValue, IDUserVote
                             ) VALUES (?, ?, ?, ?)"""
            cursor.execute(song_vote,
                            (
                                playlist_id,
                                song_id,
                                vote_value,
                                user_id
                            ))
            self.cnxn.commit()
        except sqlite3.Error as e:
            print('Database Error: ', e)

    def get_song_votes(self, song_id, playlist_id):
        try:
            cursor = self.cnxn.cursor()
            song_vote_qry = """SELECT SUM(VoteValue)
                                FROM tblSongVotes
                                WHERE IDPlaylist = ? AND IDSong = ?"""
            cursor.execute(song_vote_qry,
                            (
                                playlist_id,
                                song_id
                            ))
            votes = self.rows_to_dict(cursor)
            v = votes[0]['SUM(VoteValue)']
            if v == None:
                return 0
            else:
                return v
        except sqlite3.Error as e:
            print('Database Error: ', e)

    def add_song_to_playlist(self, playlist_id, song):
        try:
            cursor = self.cnxn.cursor()
            song_insrt = """INSERT INTO tblSongs(
                          Name, Artist, Album, SpotifySongID, IDPlaylist, Duration
                        ) VALUES (?, ?, ?, ?, ?, ?)"""

            cursor.execute(song_insrt,
                       (song['name'],
                        song['artist'],
                        song['album'],
                        song['spotify_song_id'],
                        playlist_id,
                        song['duration']))
            
            self.cnxn.commit()
            return cursor.lastrowid # returns id of added song
        except sqlite3.Error as e:
            print('Database Error:', e)

    def save_user_playlist(self, playlist):
        """Saves a new user playlist with all songs"""
        cursor = self.cnxn.cursor()
        sp_id = playlist['spotify_id']
        #Get user id for playlist insert
        user_id = self.get_user_id(sp_id)

        pl_insrt = """INSERT INTO tblPlaylists(
                      Name, Description, DateCreated, AccessCode, Public, IDUser
                    ) VALUES (?, ?, date('now'), ?, ?, ?)"""

        # Insert playlist record into DB
        cursor.execute(pl_insrt,
                       playlist['name'],
                       playlist['description'],
                       playlist['AccessCode'],
                       playlist['public'],
                       user_id)

        # Get playlist ID for song inserts
        playlist_id = cursor.execute('SELECT last_insert_rowid();').fetchone()

        song_insrt = """INSERT INTO tblSongs(
                      Name, spotifyId, IDPlaylist
                    ) VALUES (?, ?, ?)"""

        # Insert songs into DB
        for song in playlist['songs']:
            cursor.execute(song['name'],
                           song['spotify_id'],
                           playlist_id)
        
        # Commit the transaction
        self.cnxn.commit()

    def save_playlist(self, playlist):
        cursor = self.cnxn.cursor()
        sp_id = playlist['spotify_id']
        #Get user id for playlist insert
        user_id = self.get_user_id(sp_id)

        pl_insrt = """INSERT INTO tblPlaylists(
                      Name, Description, DateCreated, AccessCode, Public, IDUser
                    ) VALUES (?, ?, date('now'), ?, ?, ?)"""

        # Insert playlist record into DB
        
        values = [
            playlist['name'],
            playlist['description'],
            playlist['access_code'],
            1,
            user_id,
        ]

        cursor.execute(pl_insrt, values)
        self.cnxn.commit()

    def delete_playlist(self, playlist_id):
        song_del = """DELETE FROM tblSongs
                      WHERE IDPlaylist = ?"""
        playlist_del = """DELETE FROM tblPlaylists
                          WHERE IDPlaylist = ?"""
        songvote_del = """DELETE FROM tblSongVotes
                          WHERE IDPlaylist = ?"""

        cursor = self.cnxn.cursor()
        cursor.execute(song_del, [playlist_id])
        cursor.execute(playlist_del, [playlist_id])
        cursor.execute(songvote_del, [playlist_id])
        self.cnxn.commit()

    def delete_song_from_playlist(self, playlist_id, song_id):
        song_del = """DELETE FROM tblSongs
                      WHERE IDPlaylist = ? AND SpotifySongID = ?"""
        cursor = self.cnxn.cursor()
        cursor.execute(song_del, [playlist_id, song_id])
        self.cnxn.commit()

    def get_playlist(self, playlist_id):
        qry_playlist = """SELECT  tblSongs.IDSong AS id,
                                  tblSongs.Name AS name,
                                  tblSongs.Artist AS artist,
                                  tblSongs.Album AS album,
                                  tblSongs.SpotifySongID AS spotify_song_id,
                                  tblSongs.IDPlaylist AS playlist_id,
                                  tblSongs.Duration AS duration,
                                  COUNT(*) AS votes
                           FROM tblSongs
                             JOIN tblPlaylists
                               ON tblPlaylists.IDPlaylist = playlist_id
                             JOIN tblSongVotes
                               ON tblSongVotes.IDSong = tblSongs.IDSong
                           WHERE tblPlaylists.IDPlaylist = ?
                           GROUP BY tblSongs.IDSong,
                                    tblSongs.Name,
                                    tblSongs.Artist,
                                    tblSongs.Album,
                                    tblSongs.SpotifySongID,
                                    tblSongs.IDPlaylist"""
        cursor = self.cnxn.cursor()
        cursor.execute(qry_playlist, [playlist_id])
        pl_data = self.rows_to_dict(cursor)
        return pl_data



    def get_user_playlists(self, spotify_id):
        """Gets all user playlists for a user"""
        qry_playlists = """SELECT IDPlaylist AS id,
                                  Name AS name,
                                  Description AS description,
                                  AccessCode AS access_code,
                                  Public AS public
                           FROM tblPlaylists
                             JOIN tblUsers
                               ON tblPlaylists.IDUser = tblUsers.IDUser
                           WHERE tblUsers.SpotifyUserId = ?"""
        with self.cnxn:
            try:
                cursor = self.cnxn.execute(qry_playlists, [spotify_id])
                playlists = self.rows_to_dict(cursor)
                return playlists
            except sqlite3.Error as e:
                print('Database error:', e)
                return

    def get_playlist_name_and_access_code(self, playlist_id):
        qry_access_code = """SELECT Name, AccessCode
                                FROM tblPlaylists
                                WHERE IDPlaylist = ?"""
        with self.cnxn:
            try:
                cursor = self.cnxn.execute(qry_access_code, [playlist_id])
                access_code = self.rows_to_dict(cursor)
                return access_code
            except sqlite3.Error as e:
                print('Database error:', e)
                return

    def get_user_playlist(self, playlist_id):
        qry_playlist = """SELECT IDSong AS id,
                                  tblSongs.Name AS name,
                                  Artist AS artist,
                                  Album AS album,
                                  SpotifySongID AS spotify_song_id,
                                  Duration AS duration,
                                  tblSongs.IDPlaylist AS playlist_id
                           FROM tblSongs
                             JOIN tblPlaylists
                               ON tblPlaylists.IDPlaylist = playlist_id
                           WHERE tblPlaylists.IDPlaylist = ?"""
        with self.cnxn:
            try:
                cursor = self.cnxn.execute(qry_playlist, [playlist_id])
                playlist = self.rows_to_dict(cursor)
                return playlist
            except sqlite3.Error as e:
                print('Database error:', e)
                return

    def get_playlist_with_access_code(self, access_code):
        qry_playlist_name = """SELECT Name, AccessCode, IDPlaylist FROM tblPlaylists WHERE AccessCode = ?"""
                                  
        qry_playlist = """SELECT IDSong AS id,
                                  tblSongs.Name AS name,
                                  Artist AS artist,
                                  Album AS album,
                                  SpotifySongID AS spotify_song_id,
                                  tblSongs.IDPlaylist AS playlist_id
                           FROM tblSongs
                             JOIN tblPlaylists
                               ON tblPlaylists.IDPlaylist = playlist_id
                           WHERE tblPlaylists.AccessCode = ?"""
        with self.cnxn:
            try:
                cursor = self.cnxn.execute(qry_playlist_name, [access_code])
                playlist_name = self.rows_to_dict(cursor)
                cursor = self.cnxn.execute(qry_playlist, [access_code])
                playlist = self.rows_to_dict(cursor)
                return playlist_name + playlist
            except sqlite3.Error as e:
                print('Database error:', e)
                return

    def check_access_code_is_valid(self, access_code):
        qry_playlist_id = """SELECT IDPlaylist FROM tblPlaylists WHERE AccessCode = ?"""
        with self.cnxn:
            try:
                cursor = self.cnxn.execute(qry_playlist_id, [access_code])
                if not cursor.fetchall():
                    return False
                return True
            except sqlite3.Error as e:
                print('Database error:', e)
                return

    def update_user_token(self, spotify_id, token):
        update_token = """UPDATE tblUsers
                            SET AccessToken = ?
                          WHERE SpotifyUserId = ?
                       """
        self.execute(update_token, params=[token, spotify_id])

    def get_user_token(self, spotify_id):
        qry_token = """SELECT AccessToken FROM tblUsers WHERE SpotifyUserId = ?"""
        token = self.execute(qry_token, params=[spotify_id])
        if token:
            return token[0][0]
        return

    def get_host_token(self, playlist_id):
        qry_token = """SELECT tblUsers.AccessToken
                     FROM tblPlaylists 
                        JOIN tblUsers
                            ON tblPlaylists.IDUser = tblUsers.IDUser
                     WHERE tblPlaylists.IDPlaylist = ?"""

        token = self.execute(qry_token, params=[playlist_id])
        if token:
            return token[0][0]
        return

    def add_user(self, display_name, spotify_id, token):
        insert = """INSERT INTO tblUsers(
                      DisplayName, LastLoginDate, AccessToken, SpotifyUserId
                    ) VALUES (?, date('now'), ?, ?)
                 """
        self.execute(insert, params=[display_name, token, spotify_id])

    def rows_to_dict(self, cursor):

        cols = [col[0] for col in cursor.description]
        dataset = cursor.fetchall()
        data = []
        for row in dataset:
            data.append(dict(zip(cols, row)))

        return data


        
