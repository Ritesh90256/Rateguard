import time

class Metrics:
    def __init__(self):
        self.requests_allowed = 0
        self.requests_denied = 0
        self.errors = 0
        self.total_requests = 0
        self.total_latency = 0.0

        self.algorithm_metrics = {}
        self.tier_metrics = {}

    def record_request(self, allowed, latency, algorithm, tier):
        self.total_requests += 1

        if allowed:
            self.requests_allowed += 1
        else:
            self.requests_denied += 1

        self.total_latency += latency

        if algorithm not in self.algorithm_metrics:
            self.algorithm_metrics[algorithm] = {
                "total_requests": 0,
                "requests_allowed": 0,
                "requests_denied": 0,
                "total_latency": 0.0
            }

        algorithm_metrics = self.algorithm_metrics[algorithm]

        algorithm_metrics["total_requests"] += 1

        if allowed:
            algorithm_metrics["requests_allowed"] += 1
        else:
            algorithm_metrics["requests_denied"] += 1

        algorithm_metrics["total_latency"] += latency

        if tier not in self.tier_metrics:
            self.tier_metrics[tier] = {
                "total_requests": 0,
                "requests_allowed": 0,
                "requests_denied": 0,
                "total_latency": 0.0
            }

        tier_metrics = self.tier_metrics[tier]

        tier_metrics["total_requests"] += 1

        if allowed:
            tier_metrics["requests_allowed"] += 1
        else:
            tier_metrics["requests_denied"] += 1

        tier_metrics["total_latency"] += latency

    def record_error(self):
        self.errors += 1

    def _average_latency(self, total_latency, total_requests):
        if total_requests == 0:
            return 0.0

        return total_latency / total_requests

    def snapshot(self):
        average_latency = self._average_latency(
            self.total_latency,
            self.total_requests
        )

        algorithm_snapshot = {}

        for algorithm, metrics in self.algorithm_metrics.items():
            algorithm_snapshot[algorithm] = {
                "total_requests": metrics["total_requests"],
                "requests_allowed": metrics["requests_allowed"],
                "requests_denied": metrics["requests_denied"],
                "average_latency": self._average_latency(
                    metrics["total_latency"],
                    metrics["total_requests"]
                )
            }

        tier_snapshot = {}

        for tier, metrics in self.tier_metrics.items():
            tier_snapshot[tier] = {
                "total_requests": metrics["total_requests"],
                "requests_allowed": metrics["requests_allowed"],
                "requests_denied": metrics["requests_denied"],
                "average_latency": self._average_latency(
                    metrics["total_latency"],
                    metrics["total_requests"]
                )
            }

        return {
            "total_requests": self.total_requests,
            "requests_allowed": self.requests_allowed,
            "requests_denied": self.requests_denied,
            "errors": self.errors,
            "average_latency": average_latency,
            "algorithms": algorithm_snapshot,
            "tiers": tier_snapshot
        }


def measure_time():
    return time.perf_counter()