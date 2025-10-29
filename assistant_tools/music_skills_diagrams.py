music_pause_playback_scheme = {
    "name": "music_pause_playback",
    "description": "Pauses the currently playing music. If nothing is playing, does nothing.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

music_resume_playback_scheme = {
    "name": "music_resume_playback",
    "description": "Resumes music playback if it was paused.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

music_play_next_track_scheme = {
    "name": "music_play_next_track",
    "description": "Switches to the next track in the current playlist.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

music_play_previous_track_scheme = {
    "name": "music_play_previous_track",
    "description": "Switches to the previous track in the current playlist.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

music_clear_playlist_scheme = {
    "name": "music_clear_playlist",
    "description": "Clears the current playlist (play queue) completely.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}
 
music_play_playlist_scheme = {
    "name": "music_play_playlist",
    "description": "Finds a playlist (a folder containing music) by name and plays all tracks from it, replacing the current queue. Use when the user requests to play an artist, album, or a specific playlist.",
    "parameters": {
        "type": "object",
        "properties": {
            "playlist_name": {
                "type": "string",
                "description": "The name of the playlist, artist, or album. For example: 'Slayer', 'Daft Punk', 'Lovely tracks'",
            },
        },
        "required": ["playlist_name"],
    },
}

music_play_track_scheme = {
    "name": "music_play_track",
    "description": (
        "Finds and plays a track from the user's local music library. "
        "The library contains artists such as Slipknot, Slayer, ACDC and composers such as Pawel Blaszczak. "
        "The function uses fuzzy search, so it can correct typos in the query. "
        "Use when the user requests to play a specific song."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "track_name": {
                "type": "string",
                "description": "Song title. May contain typos. For example: 'caster', 'Psichosal'",
            },
            "artist_name": {
                "type": "string",
                "description": "The artist's name. This may not be specified. For example: 'Slipknot'",
            },
        },
    },
}

all_names_playlists_scheme = {
    "name": "all_names_playlists",
    "description": "Returns the names of all playlists.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

all_tracks_in_playlist_scheme = {
    "name": "all_tracks_in_playlist",
    "description": "Returns the names of all tracks in playlist.",
    "parameters": {
        "type": "object",
        "properties": {
            "playlist_name": {
                "type": "string",
                "description": "The name of the playlist from which you want to find out the names of all the tracks."
            },
        },
        "required": ["playlist_name"],
    },
}


