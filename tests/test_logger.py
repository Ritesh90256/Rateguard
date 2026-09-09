import json
from app.logger import log_event, logger

def test_log_event_creates_structured_json(monkeypatch):
    logged_message = {}

    def fake_info(message):
        logged_message["message"] = message

    monkeypatch.setattr(logger, "info", fake_info)

    log_event(
        "rate_limit_decision",
        client_id="Client-A",
        tier="free",
        algorithm="token_bucket",
        allowed=True,
        latency_ms=1.5,
        instance="server-1"
    )

    event = json.loads(logged_message["message"])

    assert event["event"] == "rate_limit_decision"
    assert event["client_id"] == "Client-A"
    assert event["tier"] == "free"
    assert event["algorithm"] == "token_bucket"
    assert event["allowed"] is True
    assert event["latency_ms"] == 1.5
    assert event["instance"] == "server-1"