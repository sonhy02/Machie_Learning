import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import requests

# API 요청을 통해 데이터 가져오기
url = "https://codeforces.com/api/user.rating?handle=EN_SA"
response = requests.get(url)
data = response.json()
y = [val['newRating'] for val in data['result']]
data = np.array(y).reshape(-1, 1)

x: list = []
ys: list = []
for i in range(1, len(y) - 1):
    t = np.arange(i, i + 1, 0.1)
    x.extend(t)
    ys.extend((y[i + 1] - y[i]) * t + (y[i - 1] - (y[i + 1] - y[i]) * x[-1]))

noise = np.random.normal(-5, 5, len(ys))  # Mean = 0, Stddev = 1
ys = np.array(ys) + noise
data = np.array(ys).reshape(-1, 1)

# 데이터 정규화
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)


# LSTM 학습 데이터를 생성
def create_dataset(dataset, time_step=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - time_step):
        a = dataset[i:(i + time_step), 0]
        dataX.append(a)
        dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)


time_step = 10
X, y_processed = create_dataset(scaled_data, time_step)

# 학습 및 테스트 세트로 나누기
train_size = int(len(X) * 0.7)
test_size = len(X) - train_size
X_train, X_test = X[0:train_size], X[train_size:len(X)]
y_train, y_test = y_processed[0:train_size], y_processed[train_size:len(y_processed)]

# LSTM 입력 형식으로 데이터 재구성
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# LSTM 모델 정의 및 컴파일
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

# 모델 훈련
model.fit(X_train, y_train, batch_size=50, epochs=50)

# 예측 수행
train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

# 데이터 다시 변환 (정규화 해제)
train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)
y_train = scaler.inverse_transform([y_train])
y_test = scaler.inverse_transform([y_test])

# RMSE 계산
train_score = np.sqrt(mean_squared_error(y_train[0], train_predict[:, 0]))
test_score = np.sqrt(mean_squared_error(y_test[0], test_predict[:, 0]))
print(f'Train Score: {train_score} RMSE')
print(f'Test Score: {test_score} RMSE')

# 예측 결과 시각화
train_predict_plot = np.empty_like(data, dtype=np.float32)
train_predict_plot[:, :] = np.nan
train_predict_plot[time_step:len(train_predict) + time_step, :] = train_predict

test_predict_plot = np.empty_like(data, dtype=np.float32)
test_predict_plot[:, :] = np.nan
test_predict_plot[len(train_predict) + (time_step):len(data), :] = test_predict

plt.figure(figsize=(12, 6))
plt.plot(scaler.inverse_transform(scaled_data), label='Original Data')
plt.plot(train_predict_plot, label='Train Predict')
plt.plot(test_predict_plot, label='Test Predict')
plt.title('Codeforces Rating Prediction with LSTM')
plt.xlabel('Time')
plt.ylabel('Rating')
plt.legend()
plt.show()

# 앞으로 있을 대회의 레이팅 예측
future_steps = 30  # 앞으로 예측할 미래 대회의 수
future_predictions = []

last_data = scaled_data[-time_step:]
current_step = np.array(last_data).reshape(1, time_step, 1)

for _ in range(future_steps):
    next_pred = model.predict(current_step)[0]
    future_predictions.append(next_pred)

    # 이어서 예측하기 위해 현재 스텝을 업데이트
    current_step = np.append(current_step[:, 1:, :], [[next_pred]], axis=1)

future_predictions = scaler.inverse_transform(future_predictions)

# 미래 대회 레이팅 예측 시각화
plt.figure(figsize=(12, 6))
plt.plot(scaler.inverse_transform(scaled_data), label='Original Data')
plt.plot(np.arange(len(scaled_data), len(scaled_data) + future_steps), future_predictions, label='Future Predictions',
         color='red')
plt.title('Codeforces Future Rating Prediction with LSTM')
plt.xlabel('Time')
plt.ylabel('Rating')
plt.legend()
plt.show()
