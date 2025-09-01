import json
import os
import logging

logger = logging.getLogger(__name__)

KNOWN_EVENTS_FILE = "data/known_events.json"

def load_known_events():
    try:
        if os.path.exists(KNOWN_EVENTS_FILE):
            with open(KNOWN_EVENTS_FILE, "r") as f:
                events = json.load(f)
                logger.info(f"Loaded {len(events)} known events")
                return set(events)
    except Exception as e:
        logger.error(f"Failed to load known events: {e}")
    return set()


def save_known_events(events):
    try:
        os.makedirs(os.path.dirname(KNOWN_EVENTS_FILE), exist_ok=True)
        with open(KNOWN_EVENTS_FILE, "w") as f:
            json.dump(list(events), f)
        logger.info(f"Saved {len(events)} known events")
    except Exception as e:
        logger.error(f"Failed to save known events: {e}")
