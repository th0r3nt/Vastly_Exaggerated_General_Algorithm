get_telegram_channel_info_scheme = {
    "name": "get_telegram_channel_info",
    "description": "Gets up-to-date information about a public Telegram channel: name, description, subscriber count, and recent posts. Useful for analyzing content or getting the latest news from a specific source.",
    "parameters": {
        "type": "object",
        "properties": {
            "channel_username": {
                "type": "string",
                "description": "The channel name in the format @channel_username. For example, the user's channel is called '@VEGA_and_other_heresy'. Other channels can be asked by the user or found on Telegram.",
            },
            "limit_posts": {
                "type": "integer",
                "description": "The number of recent posts to retrieve. Default: 500 (Great if you need to fully analyze someone's channel). Specify '0' if posts are not needed, '5' if the latest 5 posts are needed, and so on.",
            },
        },
        "required": ["channel_username"],
    },
}