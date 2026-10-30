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
    question_key = ("q" if "q" in dataset.column_names else "question")
    answer_key = ("a" if "a" in dataset.column_names else "answer")
    saved = 0 #счетчик для успешно сохраненных пар
    seen = set() #Множество уже встретившихся пар
    with open(OUTPUT_FILE, "w",encoding="utf-8") as out:
        for row in dataset:
            question = clean_text(row.get(question_key))
            answer = clean_text(row.get(answer_key))
            #Если вопрос/ответ пустой, то пропускаем
            if not question or not answer:
                continue
            #Слишком длинные вопросы/ответы тоже пропускаем
            if len(question)>250 or len(answer)>350:
                continue 
            key = (question.lower(), answer.lower())
            if key in seen:
                continue
            seen.add(key) #Запоминаем новую пару
            out.write(json.dumps(
                {
                    "q":question,
                    "a":answer
                },
                ensure_ascii=False
            )+"\n")
            saved+=1
            if saved >=MAX_ROWS:
                break
    print(f"Готово! Сохранено пар: {saved}")
    print(f"Файл данных: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

