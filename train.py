import json, os, random
#from collections import Counter #Счетчик частоты слов
import torch #библиотека для работы с НС
#import torch.nn as nn #Слои
#from torch.utils.data import Dataset, dataloader
import tqdm #полоса загрузки
import transformers #Возможно придется дописать

#Настройки обучения
DATA_FILE = "data/clean_dialogs.jsonl"
MODEL_DIR = "model"
MODEL_NAME = "cointegrated/rut5-small"
MAX_PAIRS = None #Сколько пар для обучения
VAL_SIZE = 500 #Сколько пар для проверки
MAX_SRC_TOKENS = 64 #Длина вопроса
MAX_TGT_TOKENS = 96 #Длина ответа
BATCH_SIZE = 16 #Количество примеров, одновр. обрабатываемых
EPOCHS = 2
LEARNING_RATE = 3e-4 #Скорость обучения

def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

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

def make_batch(pairs, tokenizer, device):
    questions = [q for q, a in pairs]
    answers = [a for q,a in pairs]
    x = tokenizer(questions, max_length = MAX_SRC_TOKENS, truncation = True, padding=True, 
                  pad_to_multiply_of = 16, return_tensors = "pt")
    y = tokenizer(answers, max_length = MAX_TGT_TOKENS, truncation = True, padding=True, 
                  pad_to_multiply_of = 16, return_tensors = "pt")
    labels = y.input_ids
    labels[labels == tokenizer.pad_token_id] = -100 #так помечаем "пустые" токены
    return x.input_ids.to(device), x.atteption_mask.to(device), labels.to(device)
    
@torch.no_grad() #Декоратор. PyTorch не запоминает вычисления при работе => меньше нагрузка и быстрее
def evaluate(model, pairs, tokenizer, device):
    #Средняя ошибка модели на проверочных весах
    model.eval() #Переводим модель в режим ответа
    losses = []
    for start in range(0, len(pairs), BATCH_SIZE):
        input_ids, attention_mask, labels = make_batch(pairs[start:start+BATCH_SIZE],
                                                       tokenizer, device)
        #input_ids и attention_mask показывает, где токены настоящие, а где добивка
        #labels - правильный ответъ
        losses.append(model(input_ids = input_ids, attention_mask=attention_mask, labels=labels).loss.item())
    return sum(losses)/max(len(losses),1) #Среднее арифметическое всех ошибок всех "батчей"


def main():
    random.seed(42) #Запоминаем текущий рандомный выбор
    torch.manual_seed(42)
    os.makedirs(MODEL_DIR, exist_ok=True) #Создаем папку для модели
    pairs = read_pairs() #Получаем список вопросов/ответов
    random.shuffle(pairs) #Перемешаем данные
    #Делим данные на тестовые(проверочные) и тренировочные(обуч.)
    val_pairs, train_pairs = pairs[:VAL_SIZE], pairs[VAL_SIZE:]
    if MAX_PAIRS:
        train_pairs = train_pairs[:MAX_PAIRS]
    print(f"Пар для обучения:{len(train_pairs)}, для проверки: {len(val_pairs)}")
    device = get_device()
    print("Устройство: ", device)
    if device.type == "cuda":
        print(f"Видеокарта: {torch.cuda.get_device_name}")
    else:
        print("Используется другое устройство")
    #Токенизатор
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast= False)
    #Автоматический выбор токенайзера, используя предобученную модель
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
    #AutoModelForSeq2SeqLM модель, на вход подается текст, на выходе тоже текст
