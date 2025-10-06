# music_skills.py
# Схемы для простых музыкальных команд (без параметров)
music_play_random_scheme = {
    "name": "music_play_random",
    "description": "Plays a random track from the user's entire music library. Use for general queries like 'play something', 'any music'.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

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

# Схемы для команд с параметрами 
music_play_playlist_scheme = {
    "name": "music_play_playlist",
    "description": "Finds a playlist (a folder containing music) by name and plays all tracks from it, replacing the current queue. Use when the user requests to play an artist, album, or a specific playlist.",
    "parameters": {
        "type": "object",
        "properties": {
            "playlist_name": {
                "type": "string",
                "description": "The name of the playlist, artist, or album. For example: 'Slayer', 'Daft Punk', 'My Workout Playlist'",
            },
        },
        "required": ["playlist_name"],
    },
}

music_play_track_scheme = {
    "name": "music_play_track",
    "description": "Searches for a specific track by title and/or artist name and plays it. You can use just the title, just the artist (to search any track), or both for a more precise search.",
    "parameters": {
        "type": "object",
        "properties": {
            "track_name": {
                "type": "string",
                "description": "Song title. Examples: 'Custer', 'Bohemian Rhapsody'",
            },
            "artist_name": {
                "type": "string",
                "description": "The name of the artist or band. For example: 'Slipknot', 'Slayer'",
            },
        },
        # Required здесь не ставим, так как функция может работать хотя бы с одним из параметров
    },
}