import time


class RateLimiter:
    def __init__(self, max_tokens: int, refill_rate: float) -> None:
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill_rate = time.monotonic()

    def consume(self, tokens):
        now = time.monotonic()
        time_since_last_refill = now - self.last_refill_rate
        self.tokens = min(
            self.max_tokens, self.tokens + time_since_last_refill * self.refill_rate
        )
        self.last_refill_rate = now

        if tokens > self.tokens:
            return False
        self.tokens -= tokens
        return True
