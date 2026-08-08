"""
Shared alert generator. Used by both the SSE stream and the legacy
/endpoints to produce raw alerts from either fake or CICIDS data.
"""
import os

from app.data.sample_alerts import make_fake_alert
from app.data.cicids_loader import make_cicids_alert
from app.store import store

DATA_MODE = os.environ.get("FLARE_DATA_MODE", "hybrid")


def generate_alert() -> dict:
    if DATA_MODE == "cicids":
        return make_cicids_alert()
    elif DATA_MODE == "hybrid":
        if os.environ.get("CICIDS_CSV_PATH"):
            return make_cicids_alert()
        return make_fake_alert() if store.count() % 3 == 0 else make_cicids_alert()
    return make_fake_alert()
