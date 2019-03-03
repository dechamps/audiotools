#!/usr/bin/python3

import argparse
from warnings import warn

import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate

argument_parser = argparse.ArgumentParser(description='Cross-correlates two signals.')
argument_parser.add_argument('--reference-wav-file', help='path to the reference WAV file', required=True)
argument_parser.add_argument('--test-wav-file', help='path to the test WAV file to be compared to the reference', required=True)
argument_parser.add_argument('--aligned-wav-file', help='write a copy of the test signal, shifted and trimmed to align with the reference signal')
args = argument_parser.parse_args()

reference_sample_rate_hz, reference_samples = wavfile.read(args.reference_wav_file)
if reference_samples.ndim != 1:
	raise RuntimeError('reference file must only have 1 channel')
test_sample_rate_hz, test_samples = wavfile.read(args.test_wav_file)
if test_samples.ndim != 1:
	raise RuntimeError('test file must only have 1 channel')
if reference_sample_rate_hz != test_sample_rate_hz:
	raise RuntimeError('reference and test files must have the same sample rate')

# Force float to ensure the FFT method is used (much faster)
cross_correlation = correlate(test_samples.astype(float), reference_samples.astype(float))
lag_samples = np.argmax(np.abs(cross_correlation)) - reference_samples.size + 1

print('Test signal is delayed by {samples} samples ({seconds} seconds) compared to the reference signal'.format(samples=lag_samples, seconds=lag_samples/reference_sample_rate_hz))

if args.aligned_wav_file is not None:
	aligned_samples = np.zeros(reference_samples.size, dtype=test_samples.dtype)
	copy_samples = aligned_samples.size

	aligned_start = -lag_samples
	if aligned_start > 0:
		warn('Test signal starts in the middle of the reference signal; will fill first {samples} samples ({seconds} seconds) of aligned signal with silence'.format(samples=aligned_start, seconds=aligned_start/reference_sample_rate_hz))
	else:
		aligned_start = 0
	copy_samples -= aligned_start

	test_end = lag_samples + aligned_samples.size
	if test_end > test_samples.size:
		missing_samples = test_end - test_samples.size
		warn('Test signal is truncated; will fill last {samples} samples ({seconds} seconds) of aligned signal with silence'.format(samples=missing_samples, seconds=missing_samples/reference_sample_rate_hz))
		test_end -= missing_samples
		copy_samples -= missing_samples

	aligned_samples[aligned_start:aligned_start+copy_samples] = test_samples[test_end-copy_samples:test_end]
	wavfile.write(args.aligned_wav_file, reference_sample_rate_hz, aligned_samples)
