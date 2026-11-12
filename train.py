"""Дообучение русской модели ruT5 на диалогах.
Запуск из папки проекта: python train.py
"""
import json
import os
import random

import torch
from tqdm import tqdm
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, get_linear_schedule_with_warmup

# -------------------- Настройки обучения --------------------
DATA_FILE = "data/clean_dialogs.jsonl"
MODEL_DIR = "model"
MODEL_NAME = "cointegrated/rut5-small"  # готовая русская модель (65 млн параметров), которую дообучаем
MAX_PAIRS = None      # сколько пар брать для обучения (None = все); для быстрого теста: 3000
VAL_SIZE = 500        # сколько пар отложить для проверки (модель на них не учится)
MAX_SRC_TOKENS = 64   # предел длины вопроса в токенах
MAX_TGT_TOKENS = 96   # предел длины ответа в токенах
BATCH_SIZE = 16       # пар за один шаг; при "out of memory" уменьшить до 8 или 4
EPOCHS = 2
LEARNING_RATE = 3e-4  # у готовой модели шаг меньше, чем у сети с нуля (было 0.001)


def get_device():
    """Выбирает ускоритель: CUDA на Windows/Linux или Metal на Apple Silicon."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    # MPS — графический ускоритель Apple Silicon (M1/M2/M3 и новее).
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def read_pairs():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("Сначала запусти: python prepare_data.py")
    pairs = []
    with open(DATA_FILE, encoding="utf-8") as file:
        for line in file:
            row = json.loads(line)
            question = row["q"].strip()
            answer = row["a"].strip()
            if question and answer:
                pairs.append((question, answer))
    if not pairs:
        raise RuntimeError("В файле данных нет диалоговых пар.")
    return pairs


def make_batch(pairs, tokenizer, device):
    """Превращает список пар (вопрос, ответ) в тензоры для модели."""
    questions = [q for q, a in pairs]
    answers = [a for q, a in pairs]
    # padding=True: короткие тексты добиваются пустыми токенами до длины самого длинного.
    # pad_to_multiple_of=16: длина округляется вверх до кратной 16 — так форм тензоров
    # меньше, и на Mac (Metal) обучение не тормозит из-за постоянных перекомпиляций.
    x = tokenizer(questions, max_length=MAX_SRC_TOKENS, truncation=True,
                  padding=True, pad_to_multiple_of=16, return_tensors="pt")
    y = tokenizer(answers, max_length=MAX_TGT_TOKENS, truncation=True,
                  padding=True, pad_to_multiple_of=16, return_tensors="pt")
    labels = y.input_ids
    # Пустые добавочные токены не должны влиять на ошибку: помечаем их -100 ("игнорировать").
    labels[labels == tokenizer.pad_token_id] = -100
    return x.input_ids.to(device), x.attention_mask.to(device), labels.to(device)


@torch.no_grad()
def evaluate(model, pairs, tokenizer, device):
    """Средняя ошибка модели на проверочных парах (веса не меняются)."""
    model.eval()
    losses = []
    for start in range(0, len(pairs), BATCH_SIZE):
        input_ids, attention_mask, labels = make_batch(pairs[start:start + BATCH_SIZE], tokenizer, device)
        losses.append(model(input_ids=input_ids, attention_mask=attention_mask, labels=labels).loss.item())
    return sum(losses) / max(len(losses), 1)


def main():
    random.seed(42)
    torch.manual_seed(42)
    os.makedirs(MODEL_DIR, exist_ok=True)

    pairs = read_pairs()
    random.shuffle(pairs)                      # перемешиваем ДО разделения
    val_pairs, train_pairs = pairs[:VAL_SIZE], pairs[VAL_SIZE:]
    if MAX_PAIRS:
        train_pairs = train_pairs[:MAX_PAIRS]
    print(f"Пар для обучения: {len(train_pairs)}, для проверки: {len(val_pairs)}")

    device = get_device()
    print("Устройство:", device)
    if device.type == "cuda":
        print("Видеокарта:", torch.cuda.get_device_name(0))
    elif device.type == "mps":
        print("Используется графический ускоритель Apple Metal (MPS).")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

    steps_per_epoch = (len(train_pairs) + BATCH_SIZE - 1) // BATCH_SIZE
    total_steps = steps_per_epoch * EPOCHS
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    # Планировщик: первые 3% шагов скорость обучения растёт с нуля, потом плавно падает до нуля.
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(total_steps * 0.03), num_training_steps=total_steps)

    best_val_loss = float("inf")
    for epoch in range(EPOCHS):
        random.shuffle(train_pairs)
        model.train()
        progress = tqdm(range(steps_per_epoch), desc=f"Эпоха {epoch + 1}/{EPOCHS}")
        for step in progress:
            batch = train_pairs[step * BATCH_SIZE:(step + 1) * BATCH_SIZE]
            input_ids, attention_mask, labels = make_batch(batch, tokenizer, device)
            optimizer.zero_grad(set_to_none=True)
            # 1) прямой проход: модель отвечает и сама считает ошибку (loss)
            loss = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels).loss
            # 2) обратный проход: считаем, как менять каждый вес, чтобы ошибка упала
            loss.backward()
            # 3) защита от слишком резких скачков весов
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            # 4) меняем веса и обновляем скорость обучения
            optimizer.step()
            scheduler.step()
            progress.set_postfix(loss=f"{loss.item():.3f}")

        val_loss = evaluate(model, val_pairs, tokenizer, device)
        print(f"Эпоха {epoch + 1}: ошибка на проверочных данных = {val_loss:.4f}")
        if val_loss < best_val_loss:           # стало лучше -> сохраняем
            best_val_loss = val_loss
            model.save_pretrained(MODEL_DIR)
            tokenizer.save_pretrained(MODEL_DIR)
            print("Модель сохранена в папку", MODEL_DIR)

    # Проба: несколько ответов обученной модели
    model.eval()
    for text in ["Привет!", "Как дела?", "Мне грустно"]:
        enc = tokenizer(text, return_tensors="pt").to(device)
        out = model.generate(**enc, max_new_tokens=48)
        print("Вы:", text, "| Бот:", tokenizer.decode(out[0], skip_special_tokens=True))


if __name__ == "__main__":
    main()
