"""
Platform to get if is school vaction for Home Assistant.

Document will come soon...
"""
import logging
import codecs
import datetime
import json
#from time import strptime
import jicson
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_SCAN_INTERVAL, CONF_RESOURCES)
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=60)
SENSOR_PREFIX = 'School '
FRIDAY = 'friday'

SENSOR_TYPES = {
    'is_vacation': ['mdi:school', 'is_vacation'],
    'summary': ['mdi:rename-box', 'summary'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(FRIDAY): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the shabbat config sensors."""
    friday = config.get(FRIDAY)
    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [
                sensor_type.title(), '', 'mdi:flash']

        entities.append(School_holidays(sensor_type, friday))

    add_entities(entities)


# pylint: disable=abstract-method

class School_holidays(Entity):
    """Representation of a israel school vaction."""
    school_db = None
    start = None
    end = None
    now = datetime.date.today()
    summary_name = None

    def __init__(self, sensor_type, friday):
        """Initialize the sensor."""
        self.type = sensor_type
        self.friday = friday
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][0]
        self._state = None
        self.create_db()


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    def summary_name_get(self):
        """Return the name of the sensor."""
        self.is_vacation()
        return self.summary_name

    def summary_name_set(self, string):
        """Return the name of the sensor."""
        self.summary_name = string

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """update our sensor state."""
        if self.type.__eq__('is_vacation'):
            self._state = self.is_vacation()
        elif self.type.__eq__('summary'):
            self._state = self.summary_name_get()

    def create_db(self):
        """Create clean DB file."""
        url = "http://hinuch.education.gov.il/lernet/chufshot.ics?ochlusia=2&chag=1"
        result = jicson.fromWeb(url, "")
        data_parse = str(result)
        data_parse = data_parse.replace("\\r", "").replace("\\u", "")
        result = eval(data_parse)
        for data in result['VEVENT']:
            data.pop('SEQUENCE', None)
            data.pop('UID', None)
            data.pop('DTSTAMP', None)
            data['START'] = data.pop('DTSTART;VALUE=DATE')
            data['END'] = data.pop('DTEND;VALUE=DATE')
        with codecs.open('scholl.json', 'w', encoding='utf-8') as outfile:
            json.dump(result['VEVENT'], outfile, skipkeys=False, ensure_ascii=False,
                      indent=4, separators=None, default=None, sort_keys=True)
        self.run_db()

    def run_db(self):
        """upload db from json file."""
        with open('scholl.json', encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
        self.school_db = data

    def is_vacation(self):
        """Check if it is school day."""
        if self.school_db is None:
            self.run_db()
        self.now = datetime.date.today()
        if self.now.isoweekday() != 6 and self.is_friday:
            for extract_data in self.school_db:
                self.start = datetime.datetime.strptime(str(extract_data['START']), '%Y%m%d').date()
                self.end = datetime.datetime.strptime(str(extract_data['END']), '%Y%m%d').date()
            if self.start == self.now and self.now < self.end:
                self.summary_name_set(str(extract_data['SUMMARY']))
                return 'True'
        if self.now == 6:
            self.summary_name_set("יום שבת")
        else:
            self.summary_name_set("יום לימודים")
        return 'False'

    def is_friday(self):
        """check if need to check for friday also."""
        if self.friday.__eq__("True"):
            if self.now.isoweekday() == 5:
                return True
        return False
