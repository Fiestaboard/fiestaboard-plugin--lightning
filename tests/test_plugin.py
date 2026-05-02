"""Tests for the lightning plugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from plugins.lightning import LightningPlugin
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "lightning",
    "name": "Weather Alerts",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "state": {
                "type": "string",
                "title": "US State",
                "description": "Two-letter US state code to filter alerts (e.g. CA, NY, TX).",
                "default": "CA",
                "minLength": 2,
                "maxLength": 2
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often to check for new alerts.",
                "default": 180,
                "minimum": 60
            }
        },
        "required": [
            "state"
        ]
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "event": "Severe Thunderstorm Warning",
                "headline": "...Severe Thunderstorm Warning...",
                "severity": "Severe",
                "certainty": "Observed",
                "urgency": "Immediate",
                "description": "NOAA NWS: Severe thunderstorm warning in effect.",
                "areaDesc": "Southern CA"
            }
        }
    ]
}
""")


@pytest.fixture
def plugin():
    return LightningPlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = LightningPlugin(MANIFEST)
    p.config = json.loads("""
{
    "state": "CA"
}
""")
    return p


class TestLightningPlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "lightning"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.lightning.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "event" in result.data, "missing variable: event"
        assert "headline" in result.data, "missing variable: headline"
        assert "severity" in result.data, "missing variable: severity"
        assert "alert_count" in result.data, "missing variable: alert_count"
        assert "all_clear" in result.data, "missing variable: all_clear"

    @patch("plugins.lightning.requests.get")
    def test_fetch_data_network_error(self, mock_get, configured_plugin):
        import requests as req_mod
        mock_get.side_effect = req_mod.exceptions.ConnectionError("network down")

        result = configured_plugin.fetch_data()

        assert result.available is False
        assert result.error is not None

    @patch("plugins.lightning.requests.get")
    def test_fetch_data_bad_json(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("bad json")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is False

