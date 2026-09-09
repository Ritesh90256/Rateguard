from fastapi.testclient import TestClient
from app.main import create_app
from app.metrics import Metrics

def test_metrics_start_at_zero():
    metrics = Metrics()

    result = metrics.snapshot()

    assert result["total_requests"] == 0
    assert result["requests_allowed"] == 0
    assert result["requests_denied"] == 0
    assert result["errors"] == 0
    assert result["average_latency"] == 0.0
    assert result["algorithms"] == {}
    assert result["tiers"] == {}


def test_metrics_record_allowed_request():
    metrics = Metrics()

    metrics.record_request(
        True,
        0.01,
        "token_bucket",
        "free"
    )

    result = metrics.snapshot()

    assert result["total_requests"] == 1
    assert result["requests_allowed"] == 1
    assert result["requests_denied"] == 0

    assert result["algorithms"]["token_bucket"]["total_requests"] == 1
    assert result["algorithms"]["token_bucket"]["requests_allowed"] == 1
    assert result["algorithms"]["token_bucket"]["requests_denied"] == 0

    assert result["tiers"]["free"]["total_requests"] == 1
    assert result["tiers"]["free"]["requests_allowed"] == 1
    assert result["tiers"]["free"]["requests_denied"] == 0


def test_metrics_record_denied_request():
    metrics = Metrics()

    metrics.record_request(
        False,
        0.02,
        "sliding_window_log",
        "pro"
    )

    result = metrics.snapshot()

    assert result["total_requests"] == 1
    assert result["requests_allowed"] == 0
    assert result["requests_denied"] == 1

    assert result["algorithms"]["sliding_window_log"]["total_requests"] == 1
    assert result["algorithms"]["sliding_window_log"]["requests_allowed"] == 0
    assert result["algorithms"]["sliding_window_log"]["requests_denied"] == 1

    assert result["tiers"]["pro"]["total_requests"] == 1
    assert result["tiers"]["pro"]["requests_allowed"] == 0
    assert result["tiers"]["pro"]["requests_denied"] == 1


def test_metrics_record_errors():
    metrics = Metrics()

    metrics.record_error()
    metrics.record_error()

    result = metrics.snapshot()

    assert result["errors"] == 2


def test_metrics_calculate_average_latency():
    metrics = Metrics()

    metrics.record_request(
        True,
        0.01,
        "token_bucket",
        "free"
    )

    metrics.record_request(
        False,
        0.03,
        "token_bucket",
        "free"
    )

    result = metrics.snapshot()

    assert result["total_requests"] == 2
    assert result["requests_allowed"] == 1
    assert result["requests_denied"] == 1
    assert result["average_latency"] == 0.02

    assert result["algorithms"]["token_bucket"]["average_latency"] == 0.02
    assert result["tiers"]["free"]["average_latency"] == 0.02


def test_metrics_track_multiple_algorithms_and_tiers():
    metrics = Metrics()

    metrics.record_request(
        True,
        0.01,
        "token_bucket",
        "free"
    )

    metrics.record_request(
        True,
        0.02,
        "sliding_window_log",
        "pro"
    )

    metrics.record_request(
        False,
        0.03,
        "sliding_window_counter",
        "enterprise"
    )

    result = metrics.snapshot()

    assert result["total_requests"] == 3
    assert result["requests_allowed"] == 2
    assert result["requests_denied"] == 1

    assert set(result["algorithms"].keys()) == {
        "token_bucket",
        "sliding_window_log",
        "sliding_window_counter"
    }

    assert set(result["tiers"].keys()) == {
        "free",
        "pro",
        "enterprise"
    }


def test_metrics_endpoint_returns_request_metrics():
    app = create_app()
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200

    data = response.json()

    assert "total_requests" in data
    assert "requests_allowed" in data
    assert "requests_denied" in data
    assert "errors" in data
    assert "average_latency" in data
    assert "algorithms" in data
    assert "tiers" in data