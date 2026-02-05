import os
from typing import Tuple
import joblib
import numpy as np

MODEL_PATH = os.getenv('MODEL_PATH', 'app/artifacts/model.joblib')

_model = None
_model_meta = None


def _train_fallback():
    # Train a lightweight RandomForest on synthetic samples if no model is present.
    try:
        from scripts.train import build_dataset
    except Exception:
        # minimal synthetic data if import fails
        import numpy as np
        X = np.zeros((10,12), dtype=float)
        y = np.array(['HUMAN']*5 + ['AI_GENERATED']*5)
        return X, y
    X, y = build_dataset(n=200)
    return X, y


def load_model():
    global _model, _model_meta
    if _model is None:
        # Try to load saved model; if missing, train fallback
        if os.path.exists(MODEL_PATH):
            data = joblib.load(MODEL_PATH)
            _model = data['model']
            _model_meta = data.get('meta', {})
        else:
            print('Model artifact not found. Training fallback model (this may take a few seconds)')
            X, y = _train_fallback()
            # Prefer RandomForest if available; otherwise use SimpleLogistic fallback
            try:
                from sklearn.ensemble import RandomForestClassifier
                clf = RandomForestClassifier(n_estimators=100)
                clf.fit(X, y)
            except Exception:
                print('scikit-learn not available; training SimpleLogistic fallback model')
                from app.simple_model import SimpleLogistic
                clf = SimpleLogistic(lr=0.5, n_iter=2000)
                clf.fit(X, y)

            _model = clf
            # persist fallback model for future runs
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump({'model': _model, 'meta': {}}, MODEL_PATH)
    return _model


def predict(feature_vector: np.ndarray) -> Tuple[str, float, dict]:
    model = load_model()
    probs = model.predict_proba(feature_vector.reshape(1, -1))[0]
    # assumes classes are ordered as model.classes_
    class_idx = int(np.argmax(probs))
    label = model.classes_[class_idx]
    confidence = float(probs[class_idx])
    return label, confidence, {'class_probs': {c: float(p) for c,p in zip(model.classes_, probs)}}


def explain(features: dict, label: str):
    # Build a short human-readable explanation based on measurable characteristics
    reasons = []
    if features.get('spec_flat_mean', 0) > 0.4:
        reasons.append('high spectral flatness (noise-like timbre)')
    if features.get('jitter', 0) < 0.005:
        reasons.append('very low pitch jitter (stable synthetic pitch)')
    if features.get('f0_std', 0) < 5:
        reasons.append('stable pitch contour')
    if features.get('shimmer', 0) < 0.02:
        reasons.append('low amplitude micro-variations')
    if not reasons:
        reasons.append('natural micro-variations and expressive prosody')
    polarity = 'likely AI-generated' if label=='AI_GENERATED' else 'likely human'
    return f'{polarity}: ' + '; '.join(reasons)
