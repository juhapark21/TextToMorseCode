import wave
import numpy as np

# Based on https://pypi.org/project/pysine/ 
# Bitrate does not need to be very high for morse code 
BITRATE = 40000

def apply_fade(waveform: np.ndarray, fade_samples: int) -> np.ndarray:
    """
    Applies linear fade-in and fade-out to the waveform.
    """
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)

    waveform[:fade_samples] *= fade_in
    waveform[-fade_samples:] *= fade_out
    return waveform

def generate_tones(frequency=440.0, durations_list=[1.0, 0.5, 1.0]):
    """
    Returns raw PCM audio data for a sequence of tones and silences.
    """
    all_data = bytearray()
    fade_duration = 0.005  
    fade_samples = int(BITRATE * fade_duration)

    for i, duration in enumerate(durations_list):
        if duration <= 0:
            continue

        points = int(BITRATE * duration)
        is_on = (i % 2 == 0)

        if is_on:
            times = np.linspace(0, duration, points, endpoint=False)
            wave_data = np.sin(times * frequency * 2 * np.pi)
            if len(wave_data) >= fade_samples * 2:
                wave_data = apply_fade(wave_data, fade_samples)
            else:
                # Skip fade if tone is too short
                pass
            data = np.array((wave_data + 1.0) * 127.5, dtype=np.uint8)
        else:
            # No sound 
            data = np.full(points, 128, dtype=np.uint8)

        all_data.extend(data)

    return bytes(all_data)

def write_wav(filename="temp.wav", frequency=440.0, durations_list=[1.0, 0.5, 1.0]):
    data = generate_tones(frequency, durations_list)
    # https://docs.python.org/3/library/wave.html 
    # https://stackoverflow.com/a/75026723/15372665 
    with wave.open(filename, 'wb') as wavefile:
        wavefile.setnchannels(1)            
        wavefile.setsampwidth(1)            
        wavefile.setframerate(int(BITRATE))  
        wavefile.writeframes(data)