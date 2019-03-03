#!/usr/bin/python3

import argparse

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import convolve

argument_parser = argparse.ArgumentParser(description='Plots the RMS amplitude of a signal over time.')
argument_parser.add_argument('--wav-file', help='path to the input WAV file', required=True)
argument_parser.add_argument('--window-size-seconds', help='size of sliding window, in seconds', type=float, default=0.01)
args = argument_parser.parse_args()

if (args.window_size_seconds <= 0):
	raise RuntimeError('invalid window size')

sample_rate_hz, samples = wavfile.read(args.wav_file)
if samples.ndim != 1:
	raise RuntimeError('input file must only have 1 channel')
samples = samples.astype(float)

samples_squared = np.square(samples)

window_size_samples = int(sample_rate_hz * args.window_size_seconds)
samples_mean_squared = convolve(samples_squared, np.ones(window_size_samples) / window_size_samples, mode='valid')
samples_rms = np.sqrt(samples_mean_squared)
samples_rms_db = 20 * np.log10(samples_rms * np.sqrt(2))  # Full-scale sine wave = 0 dBFS

figure = plt.figure()
axes = figure.add_subplot(1, 1, 1)
axes.plot(np.arange(window_size_samples, samples.size + 1) / sample_rate_hz, samples_rms_db)
axes.autoscale(axis='x', tight=True)
axes.set_xlabel('Time (seconds)')
axes.set_ylabel('Amplitude (dBFS)')
axes.grid()
plt.show()
