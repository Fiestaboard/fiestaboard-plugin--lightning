"""Display active National Weather Service severe weather alerts for your area."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

API_URL = "https://api.weather.gov/alerts/active"
USER_AGENT = "FiestaBoard Weather Alerts Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--lightning)"


class LightningPlugin(PluginBase):
    """Weather Alerts plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "lightning"

    def fetch_data(self) -> PluginResult:
        try:
            state = (self.config.get("state") or "CA").upper()[:2]

            response = requests.get(
                API_URL,
                params={"area": state},
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/geo+json",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            features = data.get("features", [])
            alert_count = len(features)

            if alert_count == 0:
                return PluginResult(
                    available=True,
                    data={
                        "event": "No active alerts",
                        "headline": "",
                        "severity": "None",
                        "alert_count": 0,
                        "all_clear": "Yes",
                    },
                )

            # Sort by severity: Extreme > Severe > Moderate > Minor
            severity_order = {"Extreme": 4, "Severe": 3, "Moderate": 2, "Minor": 1}
            features.sort(
                key=lambda f: severity_order.get(f.get("properties", {}).get("severity", ""), 0),
                reverse=True,
            )

            top = features[0]["properties"]
            event = str(top.get("event", "Unknown"))[:22]
            headline = str(top.get("headline", ""))[:22]
            severity = str(top.get("severity", "Unknown"))

            return PluginResult(
                available=True,
                data={
                    "event": event,
                    "headline": headline,
                    "severity": severity,
                    "alert_count": alert_count,
                    "all_clear": "No",
                },
            )
        except Exception as e:
            logger.exception("Error fetching weather alerts")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        state = config.get("state", "")
        if not state or len(str(state)) != 2 or not str(state).isalpha():
            errors.append("state must be a 2-letter US state code")
        return errors

    def cleanup(self) -> None:
        pass
