# 1. Примитивнейший бот (условия или кейсы)
# 2. Используем другие типы данных (словари) 
# или файлы json для расширения бота
# 3*. Добавим работу с голосом
# 4. Работа с МО

import random
user = ""
while True:
    user = input("Вы: ")
    user = user.lower()
    if user == "привет":
        answers = ["Привет!", "Добрый день!", "Приветствую"]
        print(f"Бот: {random.choice(answers)}")
    elif user == "пока":
        answers = ["Пока!","До свидания!"]
        print(f"Бот: {random.choice(answers)}")
        break
    elif user == "кто ты":
        answers = ["Бот для общения", "Чат-бот"]
        print(f"Бот: {random.choice(answers)}")
    else:
        print("Бот: Это сообщение я не понимаю")
