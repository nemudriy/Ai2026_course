import os, sys
import tkinter as tk
from tkinter import messagebox

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from train import get_device

def resource_path(relative_path):
    base = getattr(sys, "_MEIPASS", os.path.dirname
                   (os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

MODEL_PATH = resource_path("model")

class ChatWindow:
    def __init__(self, root):
        #root - корневое окно tkinter
        self.root = root
        root.title("Чат-бот")
        root.geometry("720x600")
        root.minsize(520, 420)
        if not os.path.exists(os.path.join(MODEL_PATH,"config.json")):
            messagebox.showerror("Модель не найдена", 
                                 "Сначала подготовь данные и обучи модель:" \
                                 "prepare_data->train")
            root.destroy()
            return 
        self.device = get_device()
        self.tokenizer = AutoTokenizer.from_pretrained("cointegrated/rut5-small",
                                                       use_fast = False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(self.device).eval()
        top = tk.Frame(root, padx = 10, pady = 8)
        top.pack(fill="x")
        tk.Button(top, text = "Очистить чат", command = self.clear_chat).pack(side="right")
        
