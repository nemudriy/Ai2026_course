import json
import os
import re

#pip install datasets
from datasets import load_dataset

DATASET_NAME = "GlayAI/Tiny-Russian-Dialogs"
OUTPUT_FILE = "data/clean_dialogs.jsonl"
MAX_ROWS = 5000 #Максимальное количество значений из датасета для обучения

def clean_text(value):
    #Эсли вместо текста пусто, то возвращаем пустую строку
    if value is None:
        return ""
    # Заменяем несколько пробелов, табуляцию и тд на один пробел. 
    # Стираем лишние пробелы в начале и конце
    return re.sub(r"\s+", " ", str(value)).strip()

def main():
    os.makedirs("data", exist_ok=True)
    print("Загрузка датасета.")
    dataset = load_dataset(DATASET_NAME, split = "train")
