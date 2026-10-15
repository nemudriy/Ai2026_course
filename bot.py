# 1. Примитивнейший бот (условия или кейсы)
# 2. Используем другие типы данных (словари) 
# или файлы json для расширения бота
# 3*. Добавим работу с голосом
# 4. Работа с МО

import random
import pyaspeller
import json
#pip install pyaspeller
user = ""
speller = pyaspeller.YandexSpeller()

with open("bot.json", "r",encoding = "utf-8") as f:
    bot =  json.load(f)


def filter(user_input):
    text=[]
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz"
    for c in user_input:
        if c in alphabet:
            text.append(c)
    return "".join(text)

while True:
    user = input("Вы: ")
    user = filter(user.lower())
    user = speller.spelled(user)

    if user == "привет":
        print("Бот: ", random.choice(bot.get("hello")))
    elif user == "пока":
        print("Бот:", random.choice(bot.get("bye")))
        break
    elif user == "кто ты":
        print("Бот: ", random.choice(bot.get("about")))
    else:
        print("Бот: Это сообщение я не понимаю")
