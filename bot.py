# 1. Примитивнейший бот (условия или кейсы)
# 2. Используем другие типы данных (словари) 
# или файлы json для расширения бота
# 3*. Добавим работу с голосом
# 4. Работа с МО
#pip install customtkinter
#pip install pyaspeller

import random
import pyaspeller
import json

import customtkinter as ctk
speller = pyaspeller.YandexSpeller()
ctk.set_appearance_mode("dark") #Тема dark/light

with open("bot.json", "r",encoding = "utf-8") as f:
    bot =  json.load(f)

def filter(user_input):
    text=[]
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz"
    for c in user_input:
        if c in alphabet:
            text.append(c)
    return "".join(text)


def answer(text):
    text = speller.spelled(filter(text)) #Чистим текст и прогоняем через спеллер
    for theme in bot.values():
        if text in theme["keys"]:
            return random.choice(theme["answers"])
        else:
            return "Не понимаю вашего сообщения"


while True:
    user = input("Вы: ")
    user = filter(user.lower())
    user = speller.spelled(user)

    answer = None
    for theme, data in bot.items():
        if user in data["keys"]:
            answer = random.choice(data['answers'])
            break
    if answer is None:
        print("Бот: Я не знаю ответа на этот вопрос")
    else:
        print(f"Бот {answer}")

    if user in bot["bye"]['keys']:
        break
