import datetime
import logging
from typing import Optional

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_UPDATE_FREQUENCY = 'update_frequency'
CONF_UPDATE_FREQUENCY_DEFAULT = 5

NOTIFICATION_ID = "petrol_price_tracker"
NOTIFICATION_TITLE = "Petrol Price Tracker Setup"

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Petrol Price sensor."""

    update_frequency = config[CONF_UPDATE_FREQUENCY]


    # data = FuelPriceData()
    # data.update()

    if data.error is not None:
        message = "Error: {}. Check the logs for additional information.".format(
            data.error
        )

        hass.components.persistent_notification.create(
            message, title=NOTIFICATION_TITLE, notification_id=NOTIFICATION_ID
        )
        return

    # available_fuel_types = data.get_available_fuel_types()

    add_entities(
        [
            {
                unique_id: 'petrol_price_tracker_testing',
                name: 'Petrol Price Tracker Test'
                state: 100,
                unit_of_measurement: '¢/L'
            }
        ]
    )