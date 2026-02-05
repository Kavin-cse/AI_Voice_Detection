import numpy as np

class SimpleLogistic:
    """A tiny logistic regression implemented with NumPy for environments
    where scikit-learn is unavailable. Provides fit, predict_proba, and classes_.
    """
    def __init__(self, lr=0.1, n_iter=1000, verbose=False):
        self.lr = lr
        self.n_iter = n_iter
        self.verbose = verbose
        self.w = None
        self.b = 0.0
        # classes_ order: AI_GENERATED, HUMAN
        self.classes_ = np.array(['AI_GENERATED', 'HUMAN'])

    def _sigmoid(self, z):
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        # Binary target: 1 for AI_GENERATED, 0 for HUMAN
        y_bin = (y == 'AI_GENERATED').astype(float)
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features, dtype=float)
        self.b = 0.0

        for i in range(self.n_iter):
            logits = X.dot(self.w) + self.b
            preds = self._sigmoid(logits)
            error = preds - y_bin
            grad_w = (X.T.dot(error)) / n_samples
            grad_b = np.mean(error)
            self.w -= self.lr * grad_w
            self.b -= self.lr * grad_b
            if self.verbose and (i % (self.n_iter // 10 + 1) == 0):
                loss = -np.mean(y_bin * np.log(preds + 1e-12) + (1 - y_bin) * np.log(1 - preds + 1e-12))
                print(f'iter={i} loss={loss:.6f}')
        return self

    def predict_proba(self, X):
        X = np.asarray(X, dtype=float)
        logits = X.dot(self.w) + self.b
        p_ai = self._sigmoid(logits)
        # Return shape (n_samples, 2) where columns correspond to classes_[0]=AI_GENERATED, classes_[1]=HUMAN
        return np.vstack([p_ai, 1 - p_ai]).T

    def predict(self, X):
        probs = self.predict_proba(X)
        idx = np.argmax(probs, axis=1)
        return self.classes_[idx]
