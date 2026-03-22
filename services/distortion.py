import numpy as np



#Memoryless distortion

def hard_clip(x, threshold=0.5):
    return np.clip(x, -threshold, threshold)

def soft_clip(x, gain=3):
    return np.tanh(gain * x)

def bitcrush(x, bits=4):
    levels = 2**bits
    return np.round(x * levels) / levels

def wavefold(x, threshold=0.6):
    y = x.copy()
    mask1 = y > threshold
    mask2 = y < -threshold
    
    y[mask1] = threshold - (y[mask1] - threshold)
    y[mask2] = -threshold - (y[mask2] + threshold)
    
    return y


#Bitwise logic modulation

def to_int16(x):
    return np.int16(x * 32767)

def from_int16(x):
    return x.astype(np.float32) / 32767


def xor_distortion(x, mask=0x0F0F):
    xi = to_int16(x)
    yi = xi ^ mask
    return from_int16(yi)