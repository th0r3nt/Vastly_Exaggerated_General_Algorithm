# Берем готовый официальный образ с Python 3.11
FROM python:3.11-slim

# Устанавливаем системные зависимости, которые нужны библиотекам
RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg

# Создаем рабочую папку внутри контейнера
WORKDIR /app

# Копируем туда файл с зависимостями
COPY requirements.txt .

# Устанавливаем все Python-библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВЕСЬ проект внутрь контейнера
COPY . .

# Указываем команду, которая должна запуститься при старте контейнера
CMD ["python", "main.py"]