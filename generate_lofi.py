import numpy as np
import wave
import struct

def generate_lofi_track(filename="lofi_track.wav", duration_sec=45, sample_rate=44100):
    num_samples = int(sample_rate * duration_sec)
    audio = np.zeros(num_samples, dtype=np.float32)
    
    bpm = 85
    seconds_per_beat = 60.0 / bpm
    samples_per_beat = int(sample_rate * seconds_per_beat)
    
    # Chord frequencies (Hz): Warm Lo-Fi 7th Chords
    # Cmaj7 (C4, E4, G4, B4), Am7 (A3, C4, E4, G4), Dm7 (D4, F4, A4, C5), G7 (G3, B3, D4, F4)
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [293.66, 349.23, 440.00, 523.25],  # Dm7
        [196.00, 246.94, 293.66, 349.23],  # G7
    ]
    
    t_global = np.arange(num_samples) / sample_rate
    
    # 1. Soft Rhodes / Synth Chords
    chord_duration_beats = 4
    samples_per_chord = samples_per_beat * chord_duration_beats
    
    for i in range(num_samples):
        beat_idx = int(i / samples_per_chord)
        chord = chords[beat_idx % len(chords)]
        t = (i % samples_per_chord) / sample_rate
        
        # Envelope: Gentle attack, long decay
        env = np.exp(-1.5 * t) * (1 - np.exp(-50 * t))
        
        synth_val = 0.0
        for freq in chord:
            # Main warm sine + sub-harmonic + gentle detune
            tone = 0.6 * np.sin(2 * np.pi * freq * t) + \
                   0.25 * np.sin(2 * np.pi * (freq * 1.002) * t) + \
                   0.15 * np.sin(2 * np.pi * (freq * 0.5) * t)
            synth_val += tone
            
        audio[i] += synth_val * env * 0.22
        
    # 2. Chill Lo-Fi Drums (Kick, Snare, Hi-Hat)
    total_beats = int(duration_sec / seconds_per_beat)
    for beat in range(total_beats):
        start_sample = int(beat * samples_per_beat)
        
        # Kick on beat 0, 2
        if beat % 2 == 0 or (beat % 4 == 3 and np.random.rand() > 0.5):
            k_len = int(sample_rate * 0.15)
            if start_sample + k_len < num_samples:
                t_k = np.linspace(0, 0.15, k_len)
                freq_k = 120 * np.exp(-20 * t_k) + 40
                kick_env = np.exp(-12 * t_k)
                kick_tone = np.sin(2 * np.pi * freq_k * t_k) * kick_env * 0.45
                audio[start_sample:start_sample+k_len] += kick_tone
                
        # Snare / Soft Rimshot on beat 1, 3
        if beat % 2 == 1:
            s_len = int(sample_rate * 0.12)
            if start_sample + s_len < num_samples:
                t_s = np.linspace(0, 0.12, s_len)
                snare_env = np.exp(-25 * t_s)
                noise = (np.random.rand(s_len) * 2 - 1) * snare_env * 0.20
                body = np.sin(2 * np.pi * 180 * t_s) * snare_env * 0.20
                audio[start_sample:start_sample+s_len] += noise + body
                
        # Hi-hat on every 8th note
        for sub in [0, 0.5]:
            hh_sample = start_sample + int(sub * samples_per_beat)
            hh_len = int(sample_rate * 0.04)
            if hh_sample + hh_len < num_samples:
                t_hh = np.linspace(0, 0.04, hh_len)
                hh_env = np.exp(-80 * t_hh)
                hh_noise = (np.random.rand(hh_len) * 2 - 1) * hh_env * (0.08 if sub == 0 else 0.05)
                audio[hh_sample:hh_sample+hh_len] += hh_noise

    # 3. Vinyl Crackle & Ambient Lo-Fi Glow
    vinyl_noise = (np.random.rand(num_samples) * 2 - 1) * 0.012
    audio += vinyl_noise

    # Normalize audio cleanly without clipping
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.85

    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        for sample in audio:
            int_sample = int(sample * 32767)
            wav_file.writeframes(struct.pack('<h', int_sample))
            
    print(f"Lo-Fi track generated: {filename} ({duration_sec}s)")

if __name__ == "__main__":
    generate_lofi_track()
