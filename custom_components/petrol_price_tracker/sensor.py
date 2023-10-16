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

ATTR_BRAND = "brand"
ATTR_UPDATED = "updated"

CONF_UPDATE_FREQUENCY = 'update_frequency'
CONF_UPDATE_FREQUENCY_DEFAULT = 5

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_UPDATE_FREQUENCY, default=CONF_UPDATE_FREQUENCY_DEFAULT): cv.positive_int,
    }
)

NOTIFICATION_ID = "petrol_price_tracker_notification"
NOTIFICATION_TITLE = "Petrol Price Tracker Setup"

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=5)


def setup_platform(hass, config, add_entities, discovery_info=None):

    update_frequency = config[CONF_UPDATE_FREQUENCY]

    data = FuelPriceData()
    data.update()

    if data.error is not None:
        message = "Error: {}. Check the logs for additional information.".format(
            data.error
        )

        hass.components.persistent_notification.create(
            message, title=NOTIFICATION_TITLE, notification_id=NOTIFICATION_ID
        )
        return
    
    for station in data.get_data():
        add_entities(
            [
                StationPriceSensor(station, data)
            ]
        )


class FuelPriceData:

    def __init__(self) -> None:
        """Initialize the sensor."""
        self._data = None
        self.error = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            res = requests.get(
                "https://petrolspy.com.au/webservice-1/station/box?neLat=-37.84907290638441&neLng=144.73212466394386&swLat=-37.975255664656636&swLng=144.5400870815464&ts=1697408601017&_=1697408600234",
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                                       'like Gecko) Chrome/80.0.3987.0 Safari/537.36 Edg/80.0.360.0'}
            )

            self._data = res.json()['message']['list']
        except requests.RequestException as exc:
            self.error = str(exc)
            _LOGGER.error("Failed to fetch Petrol Price Tracker price data. %s", exc)
            
    def get_data(self):
        return self._data

class StationPriceSensor(Entity):

    def __init__(self, station, data):
        """Initialize the sensor."""
        self._data = data
        self._name = station['name']
        self._uid = station['id']
        self._prices = station['prices']
        self._brand = station['brand']

    @property
    def unique_id(self) -> str:
       return f"petrol_price_tracker_{self._uid}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return 'Petrol Price Tracker ' + self._name

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        if self._prices['U91']:
            return self._prices['U91']['amount']
        else:
            return 0

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes of the device."""
        updatedInt = int(str(self._prices['U91']['updated'])[:10])
        updated = datetime.datetime.fromtimestamp(updatedInt)
        return {
            ATTR_BRAND: self._brand,
            ATTR_UPDATED: updated or None,
        }

    @property
    def unit_of_measurement(self) -> str:
        """Return the units of measurement."""
        return "¢/L"

    def update(self):
        """Update current conditions."""
        self._data.update()
