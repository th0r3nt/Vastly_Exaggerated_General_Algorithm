# skills_diagrams.py
get_weather_scheme = {
    "name": "get_weather", # ВАЖНО: ИМЯ ДОЛЖНО СОВПАДАТЬ С ФУНКЦИЕЙ PYTHON
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

save_to_memory_scheme = {
    "name": "save_to_memory",
    "description": "Saves a new fact or piece of information to Vega's long-term memory. Use this when the user provides important new information about themselves, their plans, projects, or asks you to remember something.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The specific, concise fact to be saved. For example: 'The user's dog is named Rex.' or 'The user is working on a post-apocalyptic car combat game.'",
            },
        },
        "required": ["text"]
    },
}

lock_pc_scheme = {
    "name": "lock_pc",
    "description": "Locks the user's workstation.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}


get_windows_layout_scheme = {
    "name": "get_windows_layout",
    "description": "Returns the current keyboard layout in Windows. Returns a string such as 'ENG', 'RUS', and so on.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

move_mouse_scheme = {
    "name": "move_mouse",
    "description": "Moves the mouse cursor to the specified X and Y coordinates on the screen.",
    "parameters": {
        "type": "object",
        "properties": {
            "x": {
                "type": "integer",
                "description": "The X-coordinate to move the mouse to."
            },
            "y": {
                "type": "integer",
                "description": "The Y-coordinate to move the mouse to."
            }
        },
        "required": ["x", "y"]
    }
}

current_mouse_coordinates_scheme = {
    "name": "current_mouse_coordinates",
    "description": "Gets the current X and Y coordinates of the mouse cursor.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

click_mouse_scheme = {
    "name": "click_mouse",
    "description": "Performs a mouse click. Can be left, right, middle, single, double, etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "button": {
                "type": "string",
                "description": "The mouse button to click: 'left', 'right', or 'middle'. Default is 'left'."
            },
            "clicks": {
                "type": "integer",
                "description": "The number of times to click. Default is 1."
            }
        }
    }
}

scroll_mouse_scheme = {
    "name": "scroll_mouse",
    "description": "Scrolls the mouse wheel up or down.",
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "The number of units to scroll. Positive for up, negative for down."
            }
        },
        "required": ["amount"]
    }
}

drag_mouse_scheme = {
    "name": "drag_mouse",
    "description": "Drags the mouse from its current position to the specified X and Y coordinates. Useful for selecting text or moving items.",
    "parameters": {
        "type": "object",
        "properties": {
            "x_to": {
                "type": "integer",
                "description": "The destination X-coordinate for the drag."
            },
            "y_to": {
                "type": "integer",
                "description": "The destination Y-coordinate for the drag."
            }
        },
        "required": ["x_to", "y_to"]
    }
}

press_hotkey_scheme = {
    "name": "press_hotkey",
    "description": "Presses a combination of keyboard keys simultaneously. For example, ('ctrl', 'c') to copy.",
    "parameters": {
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "A list of keys to press together, for example: ['alt', 'f4']"
            }
        },
        "required": ["keys"]
    }
}

copy_to_clipboard_scheme = {
    "name": "copy_to_clipboard",
    "description": "Copies the given text to the system clipboard.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to be copied."
            }
        },
        "required": ["text"]
    }
}

write_text_scheme = {
    "name": "write_text",
    "description": "Types out the given text in the currently active window. Works with any language.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to be typed."
            }
        },
        "required": ["text"]
    }
}

system_command_scheme = {
    "name": "system_command",
    "description": "Executes a system command, such as shutdown or restart. EXTREMELY DANGEROUS.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The system command to execute. For Windows: 'shutdown /s /t 1' for shutdown, 'shutdown /r /t 1' for restart."
            }
        },
        "required": ["command"]
    }
}

get_filtered_processes_scheme = {
    "name": "get_filtered_processes",
    "description": "Returns a clean list of user-run applications, filtering out system processes.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

currently_open_windows_scheme = {
    "name": "currently_open_windows",
    "description": "Returns a list of titles of all currently open windows.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

manage_window_scheme = {
    "name": "manage_window",
    "description": "Finds a window by its title and performs an action on it.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title (or part of the title) of the window to manage. For example: 'foobar2000'."
            },
            "action": {
                "type": "string",
                "description": "The action to perform: 'activate', 'minimize', 'maximize', or 'close'. Default is 'activate'."
            }
        },
        "required": ["title"]
    }
}

open_program_scheme = {
    "name": "open_program",
    "description": "Opens a program or file using its full path.",
    "parameters": {
        "type": "object",
        "properties": {
            "path_to_exe": {
                "type": "string",
                "description": "The full path to the executable or file to open. For example: 'C:\\Program Files\\...\\chrome.exe'."
            }
        },
        "required": ["path_to_exe"]
    }
}


kill_process_by_name_scheme = {
    "name": "kill_process_by_name",
    "description": "Forcibly terminates a running process by its name (e.g., 'chrome.exe'). DANGEROUS.",
    "parameters": {
        "type": "object",
        "properties": {
            "process_name": {
                "type": "string",
                "description": "The name of the process executable to kill."
            }
        },
        "required": ["process_name"]
    }
}

get_system_volume_scheme = {
    "name": "get_system_volume",
    "description": "Получает текущее значение громкости системы в процентах.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

set_system_volume_scheme = {
    "name": "set_system_volume",
    "description": "Устанавливает абсолютное значение громкости системы. Принимает значение от 0 до 100.",
    "parameters": {
        "type": "object",
        "properties": {
            "level_volume": {
                "type": "integer",
                "description": "Целевой уровень громкости в процентах (например, 50).",
            },
        },
        "required": ["level_volume"] # Явно указываем, что этот параметр обязателен
    },
}

decrease_volume_scheme = {
    "name": "decrease_volume",
    "description": "Уменьшает громкость системы на указанное значение. По умолчанию уменьшает на 10%.", 
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "Значение в процентах, на которое нужно уменьшить громкость (например, 15).",
            },
        },
        # "required" здесь не нужен, так как у amount есть значение по умолчанию (он опциональный)
    },
}

increase_volume_scheme = {
    "name": "increase_volume",
    "description": "Увеличивает громкость системы на указанное значение. По умолчанию увеличивает на 10%.",
    "parameters": {
        "type": "object",
        "properties": {
            "amount": { 
                "type": "integer",
                "description": "Значение в процентах, на которое нужно увеличить громкость (например, 20).",
            },
        },
    },
}

get_habr_news_scheme = {
    "name": "get_habr_news",
    "description": "Receives the latest news from Habr.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}

get_system_metrics_scheme = {
    "name": "get_system_metrics",
    "description": "Gets the current load, temperature of the video card, processor and RAM in the system.",
    "parameters": {
        "type": "object",
        "properties": {}
    },
}