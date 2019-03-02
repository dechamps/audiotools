# [SoX][] cheat sheet

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

[AES17-2015]: http://www.aes.org/publications/standards/search.cfm?docID=21
[IEC 61606-3:2008]: https://webstore.iec.ch/publication/5666
[ITU-R BS.468-4]: https://www.itu.int/rec/R-REC-BS.468-4-198607-I
[SoX]: http://sox.sourceforge.net/
