#!/usr/bin/python3

import argparse

import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate

argument_parser = argparse.ArgumentParser(description='Cross-correlates two signals.')
argument_parser.add_argument('--reference-wav-file', help='path to the reference WAV file', required=True)
argument_parser.add_argument('--test-wav-file', help='path to the test WAV file to be compared to the reference', required=True)
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

