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
    return "Не понимаю вашего сообщения"


def add(who, text):
    chat.configure(state="normal")
    chat.insert("end", f"{who}:{text}\n\n")
    chat.configure(state="disabled")
    chat.see("end")

def send(event=None):
    text = entry.get().strip()
    if not text:
        return
    entry.delete(0,"end")
    add("Вы: ", text)
    reply = answer(text)
    add("Бот: ", reply)
    if reply in bot["bye"]["answers"]:
        root.after(800, root.destroy)

root = ctk.CTk()
root.title("Чат-бот")
root.geometry("480x600")

#Начинаем размещать элементы (текстовое поле, поле ввода и кнопка)
#В root

chat = ctk.CTkTextbox(root, wrap = "word",font=("Segoe UI", 13))
chat.pack(fill="both",expand=True, padx=10,pady=(10,5))
chat.configure(state="disabled")

entry = ctk.CTkEntry(root, placeholder_text="Введите сообщение...")
entry.pack(fill="x", padx=(10,6), pady=(0,10), side="left", expand=True)
entry.bind("<Return>", send)

ctk.CTkButton(root, text="Отправить", width=100, 
              command=send).pack(side="right", padx=(0,10),pady=(0,10))

add("Бот", "Привет! Я простой бот, созданный для общения на разные темы")
root.mainloop()
