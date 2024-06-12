import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import requests
import math
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler


# TFModel 및 PositionalEncoding 클래스 정의
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


class TFModel(nn.Module):
    def __init__(self, iw, ow, d_model, nhead, nlayers, dropout=0.5):
        super(TFModel, self).__init__()
        self.encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=nlayers)
        self.pos_encoder = PositionalEncoding(d_model, dropout)

        self.encoder = nn.Sequential(
            nn.Linear(1, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, d_model)
        )

        self.linear = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, 1)
        )

        self.linear2 = nn.Sequential(
            nn.Linear(iw, (iw + ow) // 2),
            nn.ReLU(),
            nn.Linear((iw + ow) // 2, ow)
        )

    def generate_square_subsequent_mask(self, sz):
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

    def forward(self, src, srcmask):
        src = self.encoder(src)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src.transpose(0, 1), srcmask).transpose(0, 1)
        output = self.linear(output)[:, :, 0]
        output = self.linear2(output)
        return output


# 데이터 불러오기 및 전처리
url = "https://codeforces.com/api/user.rating?handle=tourist"
response = requests.get(url)
data = response.json()
y = [val['newRating'] for val in data['result']]

# 추가할 점 개수를 설정합니다 (여기서는 두 점 사이에 10개의 점을 추가하기로 결정).
num_new_points = 10

# 새로 확장된 데이터를 저장할 리스트를 초기화합니다.
extended_df = []

# 원본 데이터를 추가하면서 두 점 사이에 선형 보간법을 사용하여 점을 추가합니다.
for i in range(len(y) - 1):
    extended_df.extend(np.linspace(y[i], y[i + 1], num=num_new_points + 2)[:-1])

# 마지막 원래 데이터를 추가합니다.
extended_df.append(y[-1])

# 노이즈 추가
np.random.seed(42)  # 재현성을 위해 시드 설정.
noise = np.random.normal(0, 5, len(extended_df))  # 평균 0, 표준편차 5인 가우시안 노이즈 생성.
noisy_data = np.array(extended_df) + noise

# 데이터를 정규화
scaler = MinMaxScaler()
noisy_data = scaler.fit_transform(noisy_data.reshape(-1, 1)).reshape(-1)

# 시퀀스 길이 설정
input_window = 30  # 입력 길이
output_window = 1  # 출력 길이
stride = 1  # 시퀀스를 생성할 때 이동 간격


def create_sequences(data, input_window, output_window, stride):
    sequences = []
    for i in range(0, len(data) - input_window - output_window + 1, stride):
        train_seq = data[i:i + input_window]
        train_label = data[i + input_window:i + input_window + output_window]
        sequences.append((train_seq, train_label))
    return sequences


sequences = create_sequences(noisy_data, input_window, output_window, stride)


# 데이터셋을 텐서로 변환
class TimeSeriesDataset(torch.utils.data.Dataset):
    def __init__(self, sequences):
        self.sequences = sequences

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq, label = self.sequences[idx]
        return torch.Tensor(seq), torch.Tensor(label)


dataset = TimeSeriesDataset(sequences)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

# MPS 장치 사용이 가능한지 확인
device = torch.device("mps") if torch.has_mps else torch.device("cpu")
print(f"Using device: {device}")

# 모델 및 학습 설정
input_dim = 1
d_model = 512
nhead = 8
nlayers = 6
dropout = 0.1
model = TFModel(input_window, output_window, d_model, nhead, nlayers, dropout).to(device)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 학습 루프
num_epochs = 50

model.train()
for epoch in range(num_epochs):
    total_loss = 0
    for seq, label in dataloader:
        seq, label = seq.to(device), label.to(device)

        optimizer.zero_grad()
        # 시퀀스 데이터를 모델에 입력하기 위해 reshape
        src = seq.unsqueeze(-1)  # (batch_size, input_window, 1)
        src_mask = model.generate_square_subsequent_mask(input_window).to(device)
        output = model(src, src_mask)
        loss = criterion(output, label)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    avg_loss = total_loss / len(dataloader)
    print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {avg_loss:.4f}")