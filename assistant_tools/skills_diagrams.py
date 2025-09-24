# skills_diagrams.py
get_weather_scheme = {
    "name": "get_weather",
    "description": "Find the current weather in the specified city. This is necessary to answer weather questions with up-to-date data. If no city is specified, Lipetsk is the default location.",
    "parameters": {
        "type": "object",
        "properties": {
            "city_name": {
                "type": "string",
                "description": "The city for which the weather is needed. For example: Moscow.",
            },
        },
    },
}

search_in_google_scheme = {
    "name": "search_in_google",
    "description": "Searches for the given query in a search engine and opens a browser tab. Use this if you need to Google something or open a tab.",
    "parameters": {
        "type": "object",
        "properties": {
            "search_query": {
                "type": "string",
                "description": "Search query. For example: Who is Elon Musk",
            },
        },
    },
}

get_time_scheme = {
    "name": "get_time",
    "description": "Gets the current actual time.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

get_date_scheme = {
    "name": "get_date",
    "description": "Gets the current actual date.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}


make_screenshot_scheme = {
    "name": "make_screenshot",
    "description": "Takes a screenshot of the user's home screen and saves it to a file. Returns JSON with the path to the created file.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}


