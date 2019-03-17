#!/usr/bin/python3

import argparse

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import convolve

argument_parser = argparse.ArgumentParser(description='Plots the RMS amplitude of a signal over time.')
argument_parser.add_argument('--wav-file', help='path to the input WAV file', required=True)
argument_parser.add_argument('--reference-wav-file', help='use a WAV file as a reference signal')
argument_parser.add_argument('--relative', help='plot the error between the signal and the reference (if any)', action='store_true')
against_amplitude_group = argument_parser.add_mutually_exclusive_group()
against_amplitude_group.add_argument('--against-amplitude', help='plot against reference amplitude (if any), not time', action='store_true')
against_amplitude_group.add_argument('--against-normalized-amplitude', help='plot against normalized reference amplitude (if any), not time', action='store_true')
argument_parser.add_argument('--center', help='offset the Y axis such that that the median is 0 dB', action='store_true')
argument_parser.add_argument('--window-size-seconds', help='size of sliding window, in seconds', type=float, default=0.01)
args = argument_parser.parse_args()

if (args.window_size_seconds <= 0):
	raise RuntimeError('invalid window size')

def wavfile_read_normalized(wav_file):
	sample_rate_hz, samples = wavfile.read(wav_file)
	if samples.dtype.kind == 'i':
		factor = np.iinfo(samples.dtype).max
		samples = samples.astype(float)
		samples /= factor
	return sample_rate_hz, samples

sample_rate_hz, samples = wavfile_read_normalized(args.wav_file)
if samples.ndim != 1:
	raise RuntimeError('input file must only have 1 channel')

window_size_samples = int(sample_rate_hz * args.window_size_seconds)
def compute_rms_db(samples):
	samples_squared = np.square(samples)
	samples_mean_squared = np.fmax(convolve(samples_squared, np.ones(window_size_samples) / window_size_samples, mode='valid'), 1e-35)
	samples_mean_squared = samples_mean_squared[::window_size_samples]
	samples_rms = np.sqrt(samples_mean_squared)
	samples_rms_db = 20 * np.log10(samples_rms * np.sqrt(2))  # *sqrt(2) because of dBFS definition
	return samples_rms_db
samples_rms_db = compute_rms_db(samples)

figure = plt.figure()
axes = figure.add_subplot(1, 1, 1)
axes.set_ylabel('RMS amplitude (dBFS)')
axes.autoscale(axis='x', tight=True)
axes.grid()

axes.set_xlabel('Time (seconds)')
xaxis = np.arange(window_size_samples, samples.size + 1, window_size_samples) / sample_rate_hz

def plot(x, y, **kwargs):
	if args.center:
		y -= np.median(y)
	if args.against_amplitude or args.against_normalized_amplitude:
		axes.scatter(x, y, **kwargs)
	else:
		axes.plot(x, y, **kwargs)

if args.reference_wav_file is None:
	plot(xaxis, samples_rms_db)
else:
	reference_sample_rate_hz, reference_samples = wavfile_read_normalized(args.reference_wav_file)
	if reference_samples.ndim != 1:
		raise RuntimeError('reference file must only have 1 channel')
	if reference_sample_rate_hz != sample_rate_hz:
		raise RuntimError('input file and reference file must have the same sample rate')
	if reference_samples.size != samples.size:
		raise RuntimeError('input file and reference file must be the same length')
	reference_sample_rms_db = compute_rms_db(reference_samples)
	if args.against_amplitude:
		xaxis = reference_sample_rms_db
		axes.set_xlabel('Reference amplitude (dBFS)')
	if args.against_normalized_amplitude:
		xaxis = reference_sample_rms_db - np.max(reference_sample_rms_db)
		axes.set_xlabel('Normalized reference amplitude (dB)')
	if args.relative:
		axes.set_ylabel('RMS amplitude error (dB)')
		plot(xaxis, samples_rms_db - reference_sample_rms_db)
	elif args.against_amplitude or args.against_normalized_amplitude:
		plot(xaxis, samples_rms_db)
	else:
		plot(xaxis, reference_sample_rms_db, label='Reference')
		plot(xaxis, samples_rms_db, label='Signal')
		axes.legend()

plt.show()
