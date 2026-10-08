import math
import wave
import struct
import random

def make_wav(filename, duration, freq_func, vol_func):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            freq = freq_func(t)
            vol = vol_func(t)
            val = int(vol * 32767.0 * math.sin(2.0 * math.pi * freq * t))
            f.writeframesraw(struct.pack('<h', val))

# Throw sound: whoosh / slide up
make_wav('throw.wav', 0.25, lambda t: 150 + 800 * t, lambda t: max(0, 1 - 4 * t))

# Hit sound: impact (we'll just use a low frequency thump)
make_wav('hit.wav', 0.15, lambda t: 80, lambda t: max(0, 1 - 6.6 * t))
