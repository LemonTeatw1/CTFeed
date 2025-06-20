import json
import os
import logging
from src.config import KNOWN_EVENTS_FILE

logger = logging.getLogger(__name__)

def load_known_events():
    try:
        if os.path.exists(KNOWN_EVENTS_FILE):
            with open(KNOWN_EVENTS_FILE, 'r') as f:
                events = json.load(f)
                logger.info(f"載入了 {len(events)} 個已知事件")
                return set(events)
    except Exception as e:
        logger.error(f"載入已知事件失敗: {e}")
    return set()

def save_known_events(events):
    try:
        os.makedirs(os.path.dirname(KNOWN_EVENTS_FILE), exist_ok=True)
        with open(KNOWN_EVENTS_FILE, 'w') as f:
            json.dump(list(events), f)
        logger.info(f"保存了 {len(events)} 個已知事件")
    except Exception as e:
        logger.error(f"保存已知事件失敗: {e}") 