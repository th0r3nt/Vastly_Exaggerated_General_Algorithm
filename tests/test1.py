import asyncio
from pyrogram import Client

# Получаем эти данные на https://my.telegram.org/auth (API development tools)
API_ID = 22543405  # <-- ВАШ API_ID
API_HASH = "b49fd0e149ca3bdfaed576836566605b"

SESSION_NAME = "vega_telegram_session" # Имя сессии. Можно выбрать любое. Pyrogram создаст файл сессии (например, vega_telegram_session.session)
VEGA_CHANNEL_USERNAME = "@VEGA_and_other_heresy" # Канал, данные которого мы хотим получить (используем @username или ID)

async def _get_channel_data(client: Client, channel_username: str, limit_posts: int): # Функция должна быть асинхронной (async def)
    """Получает факты о канале, количество подписчиков и все посты. Сначала выводит самые актуальные посты, двигаясь к старым."""
    print(f"Запрос данных для канала: \n-> {channel_username}")

    try:
        chat = await client.get_chat(channel_username) # Все сетевые вызовы Pyrogram требуют 'await'
    except Exception as e:
        print(f"Ошибка при получении информации о чате: {e}")
        return None

    channel_info = {
        "channel_name": chat.title,
        "description": chat.description if chat.description else "No description available.",
        "subscribers": chat.members_count,
        "last_posts": []
    }

    print(f"-> Получено название: {channel_info['channel_name']} | Подписчиков: {channel_info['subscribers']}")

    # history — это асинхронный итератор, мы перебираем его
    history = client.get_chat_history(channel_username, limit=limit_posts) # Получаем историю сообщений (постов) канала
    async for message in history: # Проходимся по всем постам, используем 'async for' для асинхронного итератора
        post_data = {
            "id": message.id,
            "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
            "text": message.text.strip() if message.text else "[Media / No Text]"
        }
        channel_info["last_posts"].append(post_data)
    
    return channel_info

async def get_channel_data(channel_username: str = VEGA_CHANNEL_USERNAME, limit_posts: int = 0):
    """Основная асинхронная функция для запуска Telegram-клиента и получения данных канала."""
    async with Client(SESSION_NAME, API_ID, API_HASH) as client: # Используем 'async with' для корректного асинхронного запуска

        data = await _get_channel_data(client, channel_username, limit_posts=limit_posts) # Вызываем асинхронную функцию с 'await'

        if data:
            posts = []
            for post in data['last_posts']:
                text = post['text'].replace('\n', ' ')
                posts.append(f"ID публикации: {post['id']}; Дата публикации: {post['date']}; Текст публикации: {text}.")

            final_posts = "\n\n".join(posts)

            print(f"Название канала: {data['channel_name']}; \n\nПодписчики: {data['subscribers']}; \n\nОписание: {data['description']}; \n\nПосты: \n{final_posts}")
            return f"Название канала: {data['channel_name']}; \nПодписчики: {data['subscribers']}; \nОписание: {data['description']}; \nПосты: \n{final_posts}"

if __name__ == "__main__":
    print("Запуск клиента Telegram.")
    # Запускаем асинхронную функцию
    asyncio.run(get_channel_data())


