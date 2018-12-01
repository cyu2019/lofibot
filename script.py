from pydub import AudioSegment
import librosa
from pysndfx import AudioEffectsChain
import random
import sys
import numpy as np
from scipy.signal import butter, lfilter, freqz
import math
import time
import string
import os

#https://github.com/IIIIllllIIIIllllIIIIllllIIIIllllIIIIll/python-drums/blob/master/musical/audio/effect.py

def modulated_delay(data, modwave, dry, wet):
  ''' Use LFO "modwave" as a delay modulator (no feedback)
  '''
  out = data.copy()
  for i in range(len(data)):
    index = int(i - modwave[i])
    if index >= 0 and index < len(data):
      out[i] = data[i] * dry + data[index] * wet
  return out

def generate_wave_input(freq, length, rate=44100, phase=0.0):
  ''' Used by waveform generators to create frequency-scaled input array
  '''
  length = int(length * rate)
  phase *= float(rate) / 2
  factor = float(freq) * (math.pi * 2) / rate
  return (np.arange(length) + phase) * factor

def sine(freq, length, rate=44100, phase=0.0):
  ''' Generate sine wave for frequency of 'length' seconds long
      at a rate of 'rate'. The 'phase' of the wave is the percent (0.0 to 1.0)
      into the wave that it starts on.
  '''
  data = generate_wave_input(freq, length, rate, phase)
  return np.sin(data)

def chorus(data, freq, dry=0.5, wet=0.5, depth=1.0, delay=25.0, rate=44100):
  ''' Chorus effect
      http://en.wikipedia.org/wiki/Chorus_effect
  '''
  length = float(len(data)) / rate
  mil = float(rate) / 1000
  delay *= mil
  depth *= mil
  modwave = (sine(freq, length) / 2 + 0.5) * depth + delay
  return modulated_delay(data, modwave, dry, wet)

#https://gist.github.com/junzis/e06eca03747fc194e322
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


"""
load 2 measure sample w/ librosa
find bpm
"""


"""
use pysndfx
chorus sample
warp sample to 64bpm
create 2 edited samples:
    1 with heavy lowpass filter
    1 with regular
"""
fx = (
    AudioEffectsChain()
    .reverb()
)
infile = sys.argv[1]
sample_clean = librosa.core.load(infile, sr=44100)[0]

sample_clean = librosa.effects.time_stretch(sample_clean, (64 / float(sys.argv[2])))

sample_edit = sample_clean


#fs = 44100  # sample rate, Hz
#cutoff = 440   # desired cutoff frequency of the filter, Hz
# Filter the data, and plot both the original and filtered signals.
#sample_edit_low = butter_lowpass_filter(sample_edit, cutoff, fs)

sample_edit = chorus(sample_edit, 1) #applying chorus
sample_edit = librosa.core.resample(sample_edit, 44100, 11025) #bitcrush
sample_edit = librosa.core.resample(sample_edit, 11025, 44100) #resampling back up
#sample_bass = librosa.effects.pitch_shift(sample_clean, 44100, -12)
#sample_bass = butter_lowpass_filter(sample_bass, 300, fs)
#sample_edit = fx(sample_edit) #applying effects
token=''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(10))
librosa.output.write_wav("loop_edited"+token+".wav", sample_edit, 44100,norm=True)
#librosa.output.write_wav("loop_clean"+token+".wav", sample_edit, 44100,norm=True)
#librosa.output.write_wav("loop_bass.wav", sample_bass, 44100,norm=True)
#librosa.output.write_wav("loop_edited_low.wav", sample_edit_low, 44100,norm=True)

"""
Fade in, filtered automation 4 measures
Add drums 4 measures (A)
Filter sample 4 measures (B)
Back to A section
Remove drums, fade out 4 measures
vinyl static over all lol
"""
masterbpm = 64
millis_per_measure = int(4*60000/masterbpm)

song = AudioSegment.empty()
sample = AudioSegment.from_wav("loop_edited"+token+".wav")
sample_low = sample.low_pass_filter(440)
new_sample_rate = int(sample.frame_rate * (2.0 ** -1))
sample_bass = sample._spawn(sample.raw_data, overrides={'frame_rate': 44100})
sample_bass = sample_bass.low_pass_filter(250)
#sample_bass = AudioSegment.from_wav("loop_bass.wav")
if sys.argv[3] != "4":
	pass
elif sys.argv[3] == "2":
    sample = sample+sample
    sample_low = sample_low+sample_low
    sample_bass = sample_bass+sample_bass
else:
    quit()
sample.normalize()
sample_low.normalize()
sample_bass.normalize()

#sample = sample.overlay(sample_bass,position=0)
drums = AudioSegment.from_wav("drumloops.wav")
drumNumber = random.randint(0,3)
drums = drums[drumNumber*millis_per_measure:(drumNumber+1)*millis_per_measure-1]
drums = drums+drums
drums = drums+drums


sample_drums = drums.overlay(sample,position=0,gain_during_overlay=-4)
sample_drums = sample_drums.overlay(sample_bass,position=0,gain_during_overlay=-8)
sample_low_drums = drums.overlay(sample_low,position=0,gain_during_overlay=-6)

song += sample_low
song += sample_drums
song += sample_low_drums
song += sample_drums
song += sample_low

song = song.fade_in(duration=4*millis_per_measure)
song = song.fade_out(duration=4*millis_per_measure)

noise = random.choice([AudioSegment.from_mp3("vinyl.mp3")[:20*millis_per_measure],AudioSegment.from_mp3("rain.mp3")[:20*millis_per_measure]])
song=noise.overlay(song,gain_during_overlay=-20)
song.export("public/songs/"+token+".wav", format="wav")

os.remove("loop_edited"+token+".wav")

print("songs/"+token+".wav")

#useful command: sound1.overlay(sound2, position=0)
