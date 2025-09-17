from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from sklearn.linear_model import SGDClassifier

from ..data.types import Bar


def build_features(window: List[Bar], horizon: int = 5) -> Optional[tuple[list[float], int]]:
    if len(window) < horizon + 20:
        return None
    closes = np.array([b.close for b in window], dtype=float)
    highs = np.array([b.high for b in window], dtype=float)
    lows = np.array([b.low for b in window], dtype=float)

    # Features simples: retornos, volatilidade, posição vs SMA
    r1 = (closes[-1] - closes[-2]) / closes[-2]
    r5 = (closes[-1] - closes[-6]) / closes[-6]
    r20 = (closes[-1] - closes[-21]) / closes[-21]
    vol20 = np.std(np.diff(closes[-21:]))
    sma20 = np.mean(closes[-21:])
    dist_sma20 = (closes[-1] - sma20) / sma20

    x = [r1, r5, r20, vol20, dist_sma20]

    # Label: direção do retorno futuro em 'horizon' barras
    future = closes[-1 + horizon] if len(closes) > len(window) - 1 + horizon else None
    # Quando chamado incrementalmente, não temos futuro; faremos treino com delay
    return x, 0


@dataclass
class OnlineModel:
    horizon: int
    prob_threshold: float

    def __post_init__(self):
        self.clf = SGDClassifier(loss="log_loss", max_iter=1, learning_rate="optimal")
        self.is_warm = False
        self._xs: List[list[float]] = []
        self._ys: List[int] = []

    def update_with_window(self, past_window: List[Bar], new_label: Optional[int]) -> None:
        feat = build_features(past_window, self.horizon)
        if feat is None:
            return
        x, _ = feat
        if new_label is None:
            # Apenas armazena para alinhar quando label ficar disponível
            self._xs.append(x)
            return
        self._xs.append(x)
        self._ys.append(new_label)
        if len(self._ys) >= 50:  # começa a treinar após coletar alguns exemplos
            X = np.array(self._xs[-500:])
            y = np.array(self._ys[-500:])
            classes = np.array([0, 1])
            if not self.is_warm:
                self.clf.partial_fit(X, y, classes=classes)
                self.is_warm = True
            else:
                self.clf.partial_fit(X, y)

    def predict_proba(self, past_window: List[Bar]) -> Optional[float]:
        feat = build_features(past_window, self.horizon)
        if feat is None or not self.is_warm:
            return None
        x, _ = feat
        proba = float(self.clf.predict_proba(np.array([x]))[0][1])
        return proba

