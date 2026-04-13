import numpy as np


def fuzz(signal, gain=15.0):
    
    fuzzed_signal = np.tanh(signal * gain)
    

    return fuzzed_signal * 0.5 

