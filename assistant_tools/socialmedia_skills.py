# assistant_social_media_tools/telegram_skills.py
import asyncio
import logging
import os
from pyrogram import Client
from dotenv import load_dotenv
from assistant_general.logger_config import setup_logger
from assistant_tools.utils import play_sfx

setup_logger()
logger = logging.getLogger(__name__)

load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = "vega_telegram_session"

500

# ДЛЯ РЕГИСТРАЦИИ НОВЫХ НАВЫКОВ В ВЕГУ НУЖНО:
# Написать json схему в social_media_skills_diagrams.py
# Перейти в assistant_brain.added_skills.py и следовать инструкциям, которые описаны в файле

async def _get_telegram_channel_data(client: Client, channel_username: str, limit_posts: int):
    """Внутренняя асинхронная функция, которая делает всю работу с Pyrogram."""
    try:
        chat = await client.get_chat(channel_username)
        play_sfx('silent_execution')
    except Exception as e:
        logger.error(f"Ошибка при получении информации о чате Telegram: {e}")
        play_sfx('error')
        return f"Error: Failed to get channel information {channel_username}: {e}"

    channel_info = {
        "channel_name": chat.title,
        "description": chat.description if chat.description else "Description not available.",
        "subscribers": chat.members_count,
        "posts": []
    }

    if limit_posts > 0:
        logger.info(f"Number of posts in channel {channel_username} to analyze: {limit_posts}.")
        history = client.get_chat_history(channel_username, limit=limit_posts)

        async for message in history: # Проходимся по всем постам, используем 'async for' для асинхронного итератора
            text = message.text or message.caption or "[No Text/Media only]" # В случае ошибок заменить на text = message.text.strip() if message.text else "[Media/No Text]"
            date = message.date.strftime('%Y-%m-%d %H:%M:%S')
            final_text = text.replace('\n', ' ')
            channel_info["posts"].append(f"Post ID: {message.id}; Date: {date}; Text: {final_text}")

    play_sfx('silent_execution')
    return channel_info

# Синхронная обертка для вызова из skills_registry
def get_telegram_channel_info(channel_username: str, limit_posts: int = 500):
    """Запускает асинхронный код и возвращает готовый результат в виде строки. Принимает имя канала в формате @channel_name и количество постов."""
    MODULE_DIR = os.path.dirname(os.path.abspath(__file__)) # Папка, где лежит этот файл

    async def main():
        if not API_ID or not API_HASH:
            logger.critical("API_ID или API_HASH не найдены в .env файле!")
            return "Critical error: Telegram credentials are not configured."
            
        # Указываем workdir='.', чтобы .session файл создавался в корневой папке
        async with Client(SESSION_NAME, api_id=int(API_ID), api_hash=API_HASH, workdir=MODULE_DIR) as client:
            return await _get_telegram_channel_data(client, channel_username, limit_posts)

    try:
        data = asyncio.run(main()) # asyncio.run() - "мост" между синхронностью и асинхронностью
        
        # Красиво форматируем результат для Gemini
        if isinstance(data, dict): # Если данные - словарь с информацией о канале
            posts_str = "\n".join([f"{post}" for post in data['posts']]) 
            result_string = (f"Information about '{data['channel_name']}':\n"
                             f"Subscribers: {data['subscribers']}\n"
                             f"Description: {data['description']}\n"
                             f"\nLatest posts:\n{posts_str if posts_str else 'Posts were not requested.'}")
            logger.info(f"Successfully retrieved data for channel {channel_username}")
            play_sfx('silent_execution')
            return result_string
        else:
            return str(data) # Возвращаем сообщение об ошибке, если оно есть

    except Exception as e:
        logger.error(f"Critical error while running Telegram asynchronous task: {e}")
        play_sfx('error')
        return f"Error: Failed to execute Telegram request: {e}"


if __name__ == "__main__":
    # Тестовый вызов
    test_result = get_telegram_channel_info("@VEGA_and_other_heresy")
    print(test_result)