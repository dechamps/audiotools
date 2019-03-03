#!/usr/bin/python3

import argparse

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import convolve

argument_parser = argparse.ArgumentParser(description='Plots the RMS amplitude of a signal over time.')
argument_parser.add_argument('--wav-file', help='path to the input WAV file', required=True)
argument_parser.add_argument('--reference-wav-file', help='use a WAV file as a reference signal')
argument_parser.add_argument('--window-size-seconds', help='size of sliding window, in seconds', type=float, default=0.01)
args = argument_parser.parse_args()

if (args.window_size_seconds <= 0):
	raise RuntimeError('invalid window size')

sample_rate_hz, samples = wavfile.read(args.wav_file)
if samples.ndim != 1:
	raise RuntimeError('input file must only have 1 channel')

window_size_samples = int(sample_rate_hz * args.window_size_seconds)
def compute_rms_db(samples):
	samples = samples.astype(float)
	samples_squared = np.square(samples)
	samples_mean_squared = convolve(samples_squared, np.ones(window_size_samples) / window_size_samples, mode='valid')
	samples_rms = np.sqrt(samples_mean_squared)
	samples_rms_db = 20 * np.log10(samples_rms)
	return samples_rms_db
samples_rms_db = compute_rms_db(samples)

figure = plt.figure()
axes = figure.add_subplot(1, 1, 1)
time_seconds = np.arange(window_size_samples, samples.size + 1) / sample_rate_hz
if args.reference_wav_file is not None:
	reference_sample_rate_hz, reference_samples = wavfile.read(args.reference_wav_file)
	if reference_samples.ndim != 1:
		raise RuntimeError('reference file must only have 1 channel')
	if reference_sample_rate_hz != sample_rate_hz:
		raise RuntimError('input file and reference file must have the same sample rate')
	if reference_samples.size != samples.size:
		raise RuntimeError('input file and reference file must be the same length')
	reference_sample_rms_db = compute_rms_db(reference_samples)
	axes.plot(time_seconds, reference_sample_rms_db, label='Reference')
axes.plot(time_seconds, samples_rms_db, label='Signal')

axes.set_xlabel('Time (seconds)')
axes.set_ylabel('RMS amplitude (dB)')
axes.autoscale(axis='x', tight=True)
axes.grid()
axes.legend()
plt.show()
