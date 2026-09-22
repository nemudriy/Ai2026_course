# Предварительная обработка данных
# Установите через терминал 
# pip install numpy, scikit-learn
import numpy as np
from sklearn import preprocessing

input_data = np.array([[5.1, -2.9, 3.3],
                      [-1.2, 7.8, -6.1],
                      [3.9, 0.4, 2.1],
                      [7.3, -9.9, -4.5]])
# Бинаризация (разбиение данных на 0 и 1)
data_bin = preprocessing.Binarizer(threshold=0).transform(input_data)
print(data_bin)
# Исключение среднего
print("До: ")
print("Среднее значение (mean) = ", input_data.mean(axis=0))
print("Стандартное отклонение (std) = ", input_data.std(axis=0))

data_scalled = preprocessing.scale(input_data)
print("После")
print("Среднее значение (mean) = ", data_scalled.mean(axis=0))
print("Стандартное отклонение (std) = ", data_scalled.std(axis=0))

# Масштабирование

data_scaller_minmax = preprocessing.MinMaxScaler(feature_range=(0,1))
data_scalled_minmax = data_scaller_minmax.fit_transform(input_data)

print(data_scalled_minmax)

# Нормализация

# L1 - метод наименьших абсолютных значений
# L2 - метод наименьших квадратов
# L1 считается более надежным.

data_norm_l1 = preprocessing.normalize(input_data, norm = "l1")
data_norm_l2 = preprocessing.normalize(input_data, norm = "l2")

print(f"Нормализация l1 {data_norm_l1}")
print(f"Нормализация l2 {data_norm_l2}")