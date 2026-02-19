import math
import time

class OneEuroFilter:
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0, freq=30.0):
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.freq = float(freq)
        self.x_prev = None
        self.dx_prev = 0.0

    def _alpha(self, cutoff):
        tau = 1.0 / (2 * math.pi * cutoff)
        te = 1.0 / self.freq
        return 1.0 / (1.0 + tau / te)

    def apply(self, x, timestamp=None):
        if timestamp is not None and self.x_prev is not None:
            pass

        if self.x_prev is None:
            self.x_prev = x
            return x

        dx = (x - self.x_prev) * self.freq
        edx = self.dx_prev + (self._alpha(self.d_cutoff) * (dx - self.dx_prev))
        self.dx_prev = edx

        cutoff = self.min_cutoff + self.beta * abs(edx)

        x_hat = self.x_prev + (self._alpha(cutoff) * (x - self.x_prev))
        self.x_prev = x_hat
        return x_hat