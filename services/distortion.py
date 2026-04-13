import numpy as np

SAMPLE_RATE = 44100


def hard_clip(x, threshold=0.5):
    return np.clip(x, -threshold, threshold)


def soft_clip(x, gain=3):
    return np.tanh(gain * x)


def bitcrush(x, bits=4):
    levels = 2 ** bits
    return np.round(x * levels) / levels


def wavefold(x, threshold=0.05):
    y = np.copy(x)

    # Above threshold
    mask_high = x > threshold
    y[mask_high] = threshold - (x[mask_high] - threshold)

    # Below threshold
    mask_low = x < -threshold
    y[mask_low] = -threshold - (x[mask_low] + threshold)

    return y


# -----------------------------
# Bitwise logic modulation
# -----------------------------

def to_int16(x):
    scaled = (x * 32767).astype(np.int32)
    scaled = np.clip(scaled, -32768, 32767)
    return scaled.astype(np.int16)


def from_int16(x):
    return x.astype(np.float32) / 32767.0


def xor_distortion(x, mask=0x0F0F):
    xi = to_int16(x)

    # Convert to unsigned 16-bit
    unsigned = xi.astype(np.uint16)

    # XOR operation
    xored = unsigned ^ mask

    # Convert back to signed int16
    xored = xored.astype(np.int16)

    return from_int16(xored)

def tremolo(x, sr=44100, freq=5, depth=0.7):
    t = np.arange(len(x)) / sr
    lfo = 1 + depth * np.sin(2 * np.pi * freq * t)
    return x * lfo

def reverb(x, decay=0.5, delay=2000):
    y = np.copy(x)
    for i in range(delay, len(x)):
        y[i] += decay * y[i - delay]
    return y