# Weather Alerts Setup Guide

Display active National Weather Service severe weather alerts for your area.

## Overview

The Weather Alerts plugin queries the NWS Alerts API for active severe weather alerts in a configured US state or geographic area. It shows the most urgent active alert (tornado warning, severe thunderstorm, etc.). No API key required.

- API reference: https://www.weather.gov/documentation/services-web-api

### Prerequisites

No API key required. US locations only.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **Weather Alerts**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `lightning` plugin variables:
   ```
   {{{ lightning.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `lightning.event` | Alert event name (e.g. Tornado Warning) | `Tornado Warning` |
| `lightning.headline` | Short alert headline | `...Tornado Warning...` |
| `lightning.severity` | Alert severity (Extreme/Severe/Moderate/Minor) | `Extreme` |
| `lightning.alert_count` | Total number of active alerts in the state | `3` |
| `lightning.all_clear` | Yes if no active alerts | `No` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `state` | US State | Two-letter US state code to filter alerts (e.g. CA, NY, TX). | `CA` |
| `refresh_seconds` | Refresh Interval (seconds) | How often to check for new alerts. | `180` |

## Troubleshooting

- **No alerts shown** — if there are genuinely no active alerts, the display will say 'No active alerts'.
- **Wrong state** — check the two-letter state code is correct (e.g. `CA`, `NY`, `TX`).

