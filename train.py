import json, os, random, re
from collections import Counter #Счетчик частоты слов
import torch #библиотека для работы с НС
#pip install torch
import torch.nn as nn #Слои
from torch.utils.data import Dataset, dataloader
from tqdm import tqdm #полоса загрузки

#Настройки обучения
DATA_FILE = "data/clean_dialogs.jsonl"
MODEL_DIR = "model"
MAX_VOCAB = 12000 #Количество слов и знаков в словаре
MAX_LEN = 36 #Макс.длина одного вопроса или ответа в токенах
EMBED_SIZE = 128 #Вект.предст.каждого токена
HIDDEN_SIZE = 256 #Размер скрытого состояния нейросети
BATCH_SIZE = 8 #Количество примеров, одновр. обрабатываемых
EPOCHS = 2
LEARNING_RATE = 0.001 #Скорость обучения
MIN_WORD_FREQ = 2 #Мин.количество появления слов в датасете.

#Специальные обозначения
PAD = "<pad>" #Пустоты в последовательности
UNK = "<unk>" #Незнакомое слово в последовательности
BOS = "<bos>" #Начало ответа
EOS = "<eos>" #Конец ответа

#Токенизация
TOKEN_RE = re.compile(r"[а-яёa-z0-9]+|[^\w\s]",re.IGNORECASE)

def tokenize(text):
    return TOKEN_RE.findall(text.lower())

#"Привет, мир" -> "Привет" + "," + "мир"

def read_pairs():
    #Существует ли файл?
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("Файл не найден. Запусти prepare_data.py")
    pairs=[]
    with open (DATA_FILE, encoding="utf-8") as file:
        for line in file:
            row = json.loads(line) #Получаем словарь из каждой строчки файла
            question = row["q"].strip()
            answer = row["a"].strip()
            if question and answer:
                pairs.append((question, answer))
    if not pairs:
        raise RuntimeError("Диалогов нет")
    return pairs
