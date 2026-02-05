import os
import numpy as np
import joblib
from app.features import extract_features
import soundfile as sf
import tempfile

# Provide a tiny fallback for train_test_split when scikit-learn is unavailable
try:
    from sklearn.model_selection import train_test_split
except Exception:
    def train_test_split(X, y, test_size=0.2, stratify=None, random_state=42):
        X = np.asarray(X)
        y = np.asarray(y)
        rng = np.random.default_rng(random_state)
        if stratify is not None:
            # stratified split
            unique = np.unique(y)
            train_idx = []
            test_idx = []
            for u in unique:
                inds = np.where(y == u)[0]
                rng.shuffle(inds)
                n_test = max(1, int(len(inds) * test_size))
                test_idx.extend(inds[:n_test].tolist())
                train_idx.extend(inds[n_test:].tolist())
            return X[train_idx], X[test_idx], y[train_idx], y[test_idx]
        else:
            inds = np.arange(len(X))
            rng.shuffle(inds)
            n_test = int(len(inds) * test_size)
            test_idx = inds[:n_test]
            train_idx = inds[n_test:]
            return X[train_idx], X[test_idx], y[train_idx], y[test_idx]

# Create synthetic dataset
def synth_sample(duration=2.0, sr=16000, human=True):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    # base pitch
    base = 120 if human else 150
    # human has vibrato and jitter
    if human:
        jitter = 0.02 * np.sin(2*np.pi*5*t) * np.random.uniform(0.8,1.2)
        y = 0.5 * np.sin(2*np.pi*(base + jitter)*t)
        # add natural micro-variations
        y += 0.02 * np.random.randn(len(t))
    else:
        # AI: very stable pitch and cleaner timbre
        y = 0.5 * np.sin(2*np.pi*base*t)
        # add some vocoder-like harmonics
        y += 0.1 * np.sign(np.sin(2*np.pi*(base*2)*t))
        y += 0.005 * np.random.randn(len(t))
    # amplitude envelope
    env = np.linspace(0.8,1.0,len(t))
    y = y * env
    return y


def to_mp3_bytes(y, sr=16000):
    import io
    from pydub import AudioSegment
    import soundfile as sf
    buf = io.BytesIO()
    sf.write(buf, y, sr, format='WAV')
    buf.seek(0)
    audio = AudioSegment.from_wav(buf)
    out = io.BytesIO()
    audio.export(out, format='mp3')
    return out.getvalue()


def build_dataset(n=400):
    X = []
    y = []
    for _ in range(n//2):
        s = synth_sample(human=True)
        feat, _ = extract_features(s, sr=16000)
        X.append(feat)
        y.append('HUMAN')
    for _ in range(n//2):
        s = synth_sample(human=False)
        feat, _ = extract_features(s, sr=16000)
        X.append(feat)
        y.append('AI_GENERATED')
    return np.vstack(X), np.array(y)


def train_and_save():
    X, Y = build_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, stratify=Y)
    # Try to use scikit-learn RandomForest if available; otherwise fall back to pure-numpy logistic
    try:
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=200)
    except Exception:
        print('scikit-learn not available; using SimpleLogistic fallback')
        from app.simple_model import SimpleLogistic
        clf = SimpleLogistic(lr=0.5, n_iter=2000)

    clf.fit(X_train, y_train)
    try:
        preds = clf.predict(X_test)
        print(classification_report(y_test, preds))
    except Exception:
        print('Unable to print sklearn style report for fallback model')

    os.makedirs('app/artifacts', exist_ok=True)
    joblib.dump({'model': clf, 'meta': {}}, 'app/artifacts/model.joblib')
    print('Saved model to app/artifacts/model.joblib')


if __name__ == '__main__':
    train_and_save()
