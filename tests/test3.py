# Тесты подключения FastAPI сервера для обработки команд от клиента
from fastapi import FastAPI
import uvicorn

# Создаем экземпляр FastAPI
app = FastAPI()

# Создаем endpoint, которая будет слушать запросы
@app.get("/")
def read_root():
    return {"Hello": "World"} # Вместо этого он будет отдавать index.html

@app.post("/command")
def process_command(command: dict):
    user_query = command.get("query")
    print(f"Получена команда от клиента: {user_query}")
    # Здесь можно передавать user_query в "мозг" Веги
    return {"status": "Command received", "response": "Thinking..."}

if __name__ == "__main__":
    # Запускаем сервер
    # host="0.0.0.0" обязательно, Это делает сервер видимым в локальной сети
    uvicorn.run(app, host="0.0.0.0", port=8000)