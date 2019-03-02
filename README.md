# [SoX][] cheat sheet

## Definition of *dBFS*

The definition of the *dBFS* unit of measurement is [notably ambiguous][dbFS],
especially when dealing with RMS quantities.

[AES17-2015][] 3.12.1 and [IEC 61606-3:2008][] 3.4 both define 0 dBFS as the RMS
amplitude of a full-scale sine wave.

The SoX `stats` filter uses a different definition, where the maximum sample
value is defined as 0 dB, and the RMS value is derived from that. Thus, a
full-scale sine wave has an RMS amplitude of -3 dB according to SoX:

```
$ sox --null --null synth 5 sine 997 stats
Pk lev dB      -0.00
RMS lev dB     -3.01
```

Thus, to get to the dBFS value, one must add 3.01 dB to the RMS level that SoX
reports.

## Generate REW-compatible WAV files

Use the `--type wavpcm` output option.

## Generate a Dirac Pulse (unit impulse response)

Especially useful to study the effects of a digital filter.

```
sox --null dirac.wav trim 0 1s dcshift 0.9 pad 1 1
```

## [ITU-R BS.468-4][] weighting filter

The following sox filter chain will closely match the filter specified in
BS.468:

```
sox ... --rate 48000 ... \
	$(./generate_fir_filter.py \
		--frequency-response-spec-file=./bs468.txt \
		--dc-gain-db=-Inf --nyquist-gain-db=-Inf --antisymmetric \
		--sample-rate-hz=48000 --taps=63 --print-sox-fir)
```

![BS.468 filter response](bs468.png)

When using such a filter for [AES17-2015][]/[IEC 61606-3:2008][] measurements,
don't forget to add 5.6 dB of attenuation as specified in these standards:

```
gain -5.6
```

## [Dynamic range][] measurement

The following procedure is intended to measure dynamic range as defined in
[AES17-2015][] 6.4.1 and [IEC 61606-3:2008][] 6.2.3.3.

### Assumptions

- The EUT is reasonably linear up to 0 dBFS.
  - If it's not, AES17 and IEC 61606-3 diverge, because the AES17 6.2.1 *maximum
    input level* and *maximum output level*, used as reference levels, will be
	less than 0 dBFS. In contrast, IEC 61606-3 always uses a reference level of
	0 dBFS.
- The difference between the test signal frequency and the measured signal
  frequency is negligible.
  - If it's not, AES17 and IEC 61606-3 diverge, because AES17 specifies a notch
    filter set to the test signal frequency. In contrast, IEC 61606-3 5.6.3.1
	specifies an auto-tuning filter.
- The *upper band-edge frequency* is 20 kHz.

### Test signal

```
sox --null --bits 16 --rate 48000 997-60-16-48000.wav synth 30 sine 997 gain -60
```

### Measurement filter

The following filters should be applied on the measured signal:

- AES17 5.2.5 low-pass filter
- AES17 5.2.8 or IEC 61606-3 5.6.3.2.6 notch/band-reject filter
- AES17 5.2.7 or IEC 61606-3 5.6.3.2.9 weighting filter

The following command implements all of the above:

```
sox ... --null \
	rate -v 48000 \
	bandreject 997 2q \
	$(./generate_fir_filter.py \
		--frequency-response-spec-file=./bs468.txt \
		--dc-gain-db=-Inf --nyquist-gain-db=-Inf --antisymmetric \
		--sample-rate-hz=48000 --taps=63 --print-sox-fir) gain -5.6 \
	trim 1 -1 stats
```

Note: `trim 1 -1` removes invalid data at the beginning and end of the signal
that is caused by filter discontinuities. This invalid data can throw off the
final calculation.

### Interpreting the results

The `RMS lev dB` value from the above command shall be compared with the value
from a 997 Hz full-scale sine wave measurement. The difference between the two
is the dynamic range in *dB CCIR-RMS*.

For convenience, this value can be interpreted as a number of bits simply by
dividing by 6. (This is because adding one bit doubles the dynamic range, and
a factor of two is 6 dB.) For example, the dynamic range of TPDF-dithered
16/24-bit digital audio is 96/144 dB CCIR-RMS, and the above procedure will
confirm this. If sophisticated noise shaping is used instead of TPDF dither,
this measurement will reflect the improved perceived dynamic range thanks to the
weighting filter. For example, the measured value with SoX `dither -s -p 16` is
101 dB CCIR-RMS.

[AES17-2015]: http://www.aes.org/publications/standards/search.cfm?docID=21
[dbFS]: https://en.wikipedia.org/wiki/DBFS#RMS_levels
[dither]: https://en.wikipedia.org/wiki/Dither
[dynamic range]: https://en.wikipedia.org/wiki/Dynamic_range#Audio
[IEC 61606-3:2008]: https://webstore.iec.ch/publication/5666
[ITU-R BS.468-4]: https://www.itu.int/rec/R-REC-BS.468-4-198607-I
[SoX]: http://sox.sourceforge.net/
