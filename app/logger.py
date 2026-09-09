import json
import logging

logger = logging.getLogger("rateguard")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))

logger.addHandler(handler)


def log_event(event, **details):
    log_data = {
        "event": event,
        **details
    }

    logger.info(json.dumps(log_data))