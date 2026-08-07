"""Exercise the read-only ecobee requests against a real account.

Not collected by pytest. Run it by hand:

    ECOBEE_APPLICATION_KEY=... uv run python tests/live_integration.py

The first run prints a PIN to register at ecobee.com. Credentials are kept in
`~/.config/pyecobee/live_integration.json` and reused by later runs.

Only requests that read data are exercised. Nothing here changes a thermostat.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pyecobee import (
    EcobeeException,
    EcobeeService,
    JsonFileTokenStore,
    Selection,
    SelectionType,
)

logger = logging.getLogger("live_integration")

RUNTIME_REPORT_COLUMNS = (
    "auxHeat1,compCool1,fan,hvacMode,outdoorTemp,zoneAveTemp,"
    "zoneCalendarEvent,zoneClimate,zoneCoolTemp,zoneHeatTemp,zoneHvacMode"
)


def check(response, operation):
    """Fail loudly when ecobee reports anything other than success."""
    assert response.status.code == 0, (
        f"Failure while executing {operation}:\n{response.pretty_format()}"
    )


def authorize(ecobee_service):
    """Walk the one-time PIN authorization and store the credentials."""
    authorize_response = ecobee_service.authorize()

    logger.info(
        "Go to ecobee.com, log in, and open the settings tab. Enable the My "
        'Apps widget, paste "%s" into the PIN box, and click Install App. '
        "Authorize the permissions on the next screen, then press Enter here.",
        authorize_response.ecobee_pin,
    )
    input()
    ecobee_service.request_tokens()


def request_thermostats_summary(ecobee_service):
    logger.info("Requesting thermostat summary")

    response = ecobee_service.request_thermostats_summary(
        Selection(
            selection_type=SelectionType.REGISTERED,
            selection_match="",
            include_equipment_status=True,
        )
    )

    check(response, "request_thermostats_summary")
    logger.info("%s", response.pretty_format())


def request_thermostats(ecobee_service):
    logger.info("Requesting thermostats")

    response = ecobee_service.request_thermostats(
        Selection(
            selection_type=SelectionType.REGISTERED,
            selection_match="",
            include_alerts=True,
            include_equipment_status=True,
            include_events=True,
            include_location=True,
            include_program=True,
            include_runtime=True,
            include_sensors=True,
            include_settings=True,
            include_weather=True,
        )
    )

    check(response, "request_thermostats")
    logger.info("%s", response.pretty_format())

    return response.thermostat_list[0]


def request_runtime_reports(ecobee_service, thermostat):
    """Request yesterday's runtime report, in the thermostat's own time zone."""
    thermostat_time_zone = ZoneInfo(thermostat.location.time_zone)
    end_date_time = datetime.now(thermostat_time_zone).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_date_time = end_date_time - timedelta(days=1)

    logger.info(
        "Requesting runtime report from %s to %s", start_date_time, end_date_time
    )

    response = ecobee_service.request_runtime_reports(
        Selection(
            selection_type=SelectionType.THERMOSTATS,
            selection_match=thermostat.identifier,
        ),
        start_date_time=start_date_time,
        end_date_time=end_date_time,
        columns=RUNTIME_REPORT_COLUMNS,
    )

    check(response, "request_runtime_reports")
    logger.info("%s", response.pretty_format())


def request_groups(ecobee_service):
    logger.info("Requesting groups")

    response = ecobee_service.request_groups(
        Selection(selection_type=SelectionType.REGISTERED, selection_match="")
    )

    check(response, "request_groups")
    logger.info("%s", response.pretty_format())


def main():
    logging.basicConfig(
        format="%(asctime)s %(name)-24s %(levelname)-8s %(message)s",
        level=logging.DEBUG,
        stream=sys.stdout,
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    store = JsonFileTokenStore("~/.config/pyecobee/live_integration.json")
    application_key = os.environ.get("ECOBEE_APPLICATION_KEY") or input(
        "Enter the API key of your ecobee app: "
    )
    ecobee_service = EcobeeService(
        "live_integration", application_key, store.load(), store.save
    )

    try:
        if not ecobee_service.access_token:
            authorize(ecobee_service)

        logger.info(
            "Access token expires on %s, refresh token on %s",
            ecobee_service.access_token_expires_on,
            ecobee_service.refresh_token_expires_on,
        )

        request_thermostats_summary(ecobee_service)

        thermostat = request_thermostats(ecobee_service)

        request_runtime_reports(ecobee_service, thermostat)
        request_groups(ecobee_service)

        logger.info("All read requests succeeded")
    except EcobeeException:
        logger.exception("A request failed")

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
