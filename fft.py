import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.interpolate import interp1d

# CSVファイルの読み込み
df = pd.read_csv("outputdatas\\waveform_avg.csv")
df = df.drop_duplicates(subset="Time [s]")

# 時間と電圧の抽出
t = df["Time [s]"].values
v = df["Avg Voltage [V]"].values

# 等間隔に補間（FFTの前処理）
n_points = 10*len(t)  # 補間後の点数（任意）
t_uniform = np.linspace(t.min(), t.max(), n_points)
interp_func = interp1d(t, v, kind='cubic')
v_uniform = interp_func(t_uniform)

# 生データの波形表示
plt.figure(figsize=(10, 4))
plt.plot(t, v, label='Raw Voltage')
plt.plot(t_uniform, v_uniform, label='Uniform Voltage')
plt.xlabel("Time [s]")
plt.ylabel("Voltage [V]")
plt.title("Raw Voltage Waveform")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# FFTの実行
V_fft = fft(v_uniform)
freq = fftfreq(n_points, d=(t_uniform[1] - t_uniform[0]))

# 振幅のスケーリング（片側スペクトル）
amplitude = 2 * np.abs(V_fft[:n_points//2]) / n_points
freq_half = freq[:n_points//2]

# 振幅スペクトル（対数軸）の表示
plt.figure(figsize=(10, 4))
plt.semilogy(freq_half, amplitude, label='FFT Amplitude (log scale)')
plt.xlabel("Frequency [Hz]")
plt.ylabel("Amplitude [V] (log scale)")
plt.title("FFT Spectrum (Log Scale)")
plt.grid(True, which='both')
plt.xlim(0,35)
plt.legend()
plt.tight_layout()
plt.show()
