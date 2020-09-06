# -*- coding: utf-8 -*-
"""Submission Time Series.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1H8lRTetyRD9QL-41HPYQCZ6VvBuI2n3h

#**Submission Time Series**

Dataset yang saya gunakan yaitu data penjualan "harian" obat-obatan pada tahun 2014-2019 yang dapat dilihat pada https://www.kaggle.com/milanzdravkovic/pharma-sales-data.

Di dalam data ini terdapat beberapa istilah pada nama kolom, yaitu:
1. M01AB = Anti-inflammatory and antirheumatic products, non-steroids, Acetic acid derivatives and related substances
2. M01AE = Anti-inflammatory and antirheumatic products, non-steroids, Propionic acid derivatives
3. N02BA = Other analgesics and antipyretics, Salicylic acid and derivatives
4. N02BE/B = Other analgesics and antipyretics, Pyrazolones and Anilides
5. N05B = Psycholeptics drugs, Anxiolytic drugs
6. N05C = Psycholeptics drugs, Hypnotics and sedatives drugs
7. R03 = Drugs for obstructive airway diseases
8. R06 = Antihistamines for systemic use
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import Sequential
import tensorflow as tf

df = pd.read_csv('/content/drive/My Drive/pharma_sales_daily.csv')
df.info()

#cek jumlah null value
df.isnull().sum()

#Saya akan memprediksi penjualan N02BE(Other analgesics and antipyretics, Pyrazolones and Anilides)
#Oleh karena itu, saya hanya menggunakan 2 kolom (datum, N02BE)
dates = df['datum'].values
N02BE = df['N02BE'].values

#split data menjadi train, test
from sklearn.model_selection import train_test_split
date_train, date_test, N02BE_train, N02BE_test = train_test_split(dates, N02BE, test_size=0.2)
print(N02BE_train.shape)
print(N02BE_test.shape)

#mengubah data supaya dapat diterima model 
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
  series = tf.expand_dims(series, axis=-1)
  ds     = tf.data.Dataset.from_tensor_slices(series)
  ds     = ds.window(window_size + 1, shift=1, drop_remainder=True)
  ds     = ds.flat_map(lambda w: w.batch(window_size + 1))
  ds     = ds.shuffle(shuffle_buffer)
  ds     = ds.map(lambda w: (w[:-1], w[1:]))
  return ds.batch(batch_size).prefetch(1)

  
#mengubah data
windowed_train = windowed_dataset(N02BE_train, window_size=60, batch_size=100, shuffle_buffer=1000)
windowed_test = windowed_dataset(N02BE_test, window_size=60, batch_size=100, shuffle_buffer=1000)

#membuat model
model = Sequential([
                    LSTM(60, return_sequences=True),
                    LSTM(60),
                    Dense(30, activation='relu'),
                    Dense(10, activation='relu'),
                    Dense(1)
                    ])
optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer = optimizer,
              metrics = ['mae'])

#fit data dengan validation_split 0.2
history = model.fit(windowed_train, validation_data=windowed_test, epochs=100)

#cek apakah nilai mae <10% skala data
max = df['N02BE'].max()
min = df['N02BE'].min()

#train mae
print(11.7946 < (max-min)/10)

#val mae
print(10.9888 < (max-min)/10)

#plot akurasi 
import matplotlib.pyplot as plt

acc = history.history['mae']
val_acc = history.history['val_mae']

loss=history.history['loss']
val_loss=history.history['val_loss']

epochs_range = range(100) 
plt.figure(figsize=(10, 10))

#visualisasi training and validation accurancy
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training MAE Score')
plt.plot(epochs_range, val_acc, label='Validation MAE Score')
plt.legend(loc='best')
plt.title('Training and Validation MAE Score')

#visualisasi training and validation loss 
plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='best')
plt.title('Training and Validation Loss')
plt.show()