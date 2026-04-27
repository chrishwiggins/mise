from scipy.fftpack import fft
# Define a sample vibration signal
N = 600
t = np.linspace(0.0, 1.0, N)
acc = 0.1 * np.sin(50.0 * 2.0*np.pi*t) + 0.2 * np.sin(80.0 * 2.0*np.pi*t)
# Perform FFT
yf = fft(acc)
xf = np.linspace(0.0, 1.0/(2.0*(t[1]-t[0])), N//2)
plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))
plt.title('Frequency Response')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.show()

