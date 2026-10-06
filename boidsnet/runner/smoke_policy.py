"""Strict engineering stop rules; never alter confirmatory scoring rules."""


class SmokeStop(RuntimeError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def verdict_has_execution_error(verdict):
    # A wrong answer is a normal task outcome, not an engineering failure.
    return bool(verdict and verdict.get('crashed', 0))
