"""Графический чат. Работает как обычный Python-скрипт и внутри .app."""
import os
import sys
import tkinter as tk
from tkinter import messagebox

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from train import get_device


def resource_path(relative_path):
    """Путь к ресурсам: рядом со скриптом или внутри собранного приложения."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


MODEL_PATH = resource_path("model")   # папка, которую сохранил train.py


class ChatWindow:
    def __init__(self, root):
        self.root = root
        root.title("Чат бот")
        root.geometry("720x600")
        root.minsize(520, 420)
        if not os.path.exists(os.path.join(MODEL_PATH, "config.json")):
            messagebox.showerror("Модель не найдена", "Сначала подготовь данные и обучи модель: python prepare_data.py, затем python train.py")
            root.destroy()
            return
        self.device = get_device()
        self.tokenizer = AutoTokenizer.from_pretrained("cointegrated/rut5-small", use_fast = False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(self.device).eval()
        top = tk.Frame(root, padx=10, pady=8)
        top.pack(fill="x")
        tk.Label(top, text="Русский ИИ-собеседник", font=("Arial", 16, "bold")).pack(side="left")
        tk.Button(top, text="Очистить чат", command=self.clear_chat).pack(side="right")
        self.chat = tk.Text(root, wrap="word", state="disabled", font=("Arial", 11), padx=10, pady=10, bg="#f5f5f5")
        self.chat.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.chat.tag_config("user", foreground="#174ea6", spacing1=7, spacing3=7)
        self.chat.tag_config("bot", foreground="#187044", spacing1=7, spacing3=7)
        self.chat.tag_config("system", foreground="#777777", spacing1=5, spacing3=5)
        bottom = tk.Frame(root, padx=10, pady=8)
        bottom.pack(fill="x")
        self.entry = tk.Entry(bottom, font=("Arial", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.entry.bind("<Return>", lambda event: self.send())
        tk.Button(bottom, text="Отправить", command=self.send).pack(side="left", padx=(8, 0), ipady=4)
        self.write("Система", f"Модель загружена. Устройство: {self.device}. Ответы могут быть ошибочными или повторяться.", "system")
        self.entry.focus_set()

    def write(self, who, text, tag):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{who}: {text}\n\n", tag)
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def clear_chat(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")

    def reply(self, text):
        """Ответ модели. Параметры генерации определяют "характер" бота."""
        enc = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=96).to(self.device)
        with torch.no_grad():
            out = self.model.generate(
                **enc,
                do_sample=True,           # выбирать слова случайно, с учётом вероятностей
                temperature=0.6,          # ниже — осторожнее и предсказуемее, выше — смелее и хаотичнее
                top_p=0.9,                # отсекать совсем маловероятные слова
                repetition_penalty=1.1,   # штраф за повторы ("да да да")
                max_new_tokens=64,        # предельная длина ответа
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True) or "Пока не знаю, что ответить."

    def send(self):
        message = self.entry.get().strip()
        if not message:
            return
        self.entry.delete(0, "end")
        self.write("Вы", message, "user")
        try:
            self.write("Бот", self.reply(message), "bot")
        except Exception as error:
            self.write("Ошибка", str(error), "system")


if __name__ == "__main__":
    root = tk.Tk()
    ChatWindow(root)
    root.mainloop()
