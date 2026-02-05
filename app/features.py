import numpy as np

# Prefer librosa if available, but provide a lightweight fallback to avoid hard dependency
try:
    import librosa
    _HAS_LIBROSA = True
except Exception:
    _HAS_LIBROSA = False


def _safe_trim(y, sr):
    if _HAS_LIBROSA:
        return librosa.effects.trim(y)[0]
    # simple energy-based trim
    energy = np.abs(y)
    thresh = np.mean(energy) * 0.1
    idx = np.where(energy > thresh)[0]
    if idx.size == 0:
        return y
    return y[idx[0]:idx[-1]+1]


def _estimate_pitch_autocorr(y, sr):
    # crude autocorrelation pitch estimator
    y = y - np.mean(y)
    corr = np.correlate(y, y, mode='full')[len(y)-1:]
    corr[:int(sr/500)] = 0  # remove high freq
    peak = np.argmax(corr)
    if peak == 0:
        return 0.0
    f0 = sr / peak
    return float(f0)


def extract_features(y: np.ndarray, sr: int = 16000):
    y = y.astype(np.float32)
    features = {}

    # Trim
    y = _safe_trim(y, sr)

    # Pitch mean/std/jitter
    if _HAS_LIBROSA:
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=500, sr=sr)
            f0 = np.nan_to_num(f0)
            features['f0_mean'] = float(np.mean(f0))
            features['f0_std'] = float(np.std(f0))
            diffs = np.abs(np.diff(f0))
            features['jitter'] = float(np.mean(diffs) / (np.mean(f0) + 1e-8))
        except Exception:
            features['f0_mean'] = 0.0
            features['f0_std'] = 0.0
            features['jitter'] = 0.0
    else:
        f0 = _estimate_pitch_autocorr(y, sr)
        features['f0_mean'] = f0
        features['f0_std'] = 0.0
        features['jitter'] = 0.0

    # Energy / shimmer
    if _HAS_LIBROSA:
        hop_length = 512
        frame_energy = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop_length)[0]
        features['energy_mean'] = float(np.mean(frame_energy))
        features['energy_std'] = float(np.std(frame_energy))
        features['shimmer'] = float(features['energy_std'] / (features['energy_mean'] + 1e-8))
    else:
        frame_energy = np.abs(y)
        features['energy_mean'] = float(np.mean(frame_energy))
        features['energy_std'] = float(np.std(frame_energy))
        features['shimmer'] = float(features['energy_std'] / (features['energy_mean'] + 1e-8))

    # MFCCs or approximations
    if _HAS_LIBROSA:
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc_mean_0'] = float(np.mean(mfcc[0]))
        features['mfcc_std_0'] = float(np.std(mfcc[0]))
    else:
        # Use mean log-spectrum bins as a coarse replacement
        S = np.abs(np.fft.rfft(y))
        S = S + 1e-8
        logS = np.log(S)
        bins = np.array_split(logS, 13)
        bmeans = [float(np.mean(b)) for b in bins]
        features['mfcc_mean_0'] = bmeans[0]
        features['mfcc_std_0'] = float(np.std(bmeans))

    # Spectral flatness
    if _HAS_LIBROSA:
        spec_flat = librosa.feature.spectral_flatness(y=y)[0]
        features['spec_flat_mean'] = float(np.mean(spec_flat))
    else:
        S = np.abs(np.fft.rfft(y)) + 1e-12
        geo = np.exp(np.mean(np.log(S)))
        arith = np.mean(S)
        features['spec_flat_mean'] = float(geo / (arith + 1e-12))

    # Zero crossing rate
    if _HAS_LIBROSA:
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features['zcr_mean'] = float(np.mean(zcr))
    else:
        crossings = np.sum(np.abs(np.diff(np.sign(y)))) / 2
        features['zcr_mean'] = float(crossings / max(1, len(y)))

    # Duration
    features['duration'] = float(len(y) / sr)

    # Energy skew
    features['energy_skew'] = float(np.mean((frame_energy - np.mean(frame_energy))**3))

    # Return in fixed order
    keys = ['f0_mean','f0_std','jitter','shimmer','energy_mean','energy_std','mfcc_mean_0','mfcc_std_0','spec_flat_mean','zcr_mean','duration','energy_skew']
    return np.array([features[k] for k in keys], dtype=np.float32), features
