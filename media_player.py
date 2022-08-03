"""Support for Sony Receivers."""
from __future__ import annotations
import json

import logging
import requests

import voluptuous as vol

from homeassistant.components.media_player import (
    PLATFORM_SCHEMA,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_SOURCE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Sony Receiver"
DEFAULT_SOURCES: dict[str, str] = {}
DEFAULT_HEADER = {"X-Auth-PSK": "1234"}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_SOURCE, default=DEFAULT_SOURCES): {cv.string: cv.string},
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Sony Reciver platform."""
    sony_receiver = SonyDevice(
        config[CONF_NAME],
        config[CONF_HOST],
        config[CONF_SOURCE],
    )

    if sony_receiver.update():
        add_entities([sony_receiver])


class SonyDevice(MediaPlayerEntity):
    """Representation of a Sony device."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, name, host, sources):
        """Initialize the Sony device."""
        self._name = name
        self._host = host
        self._url = "http://" + host + "/sony/system"
        self._pwstate = "PWR1"
        self._volume = 0
        self._muted = False
        self._selected_source = ""

    def send_command(self,command):
        url = self._url
        """Send HTTP request to receiver"""
        if(command=="on"):
            data = {"method":"setPowerStatus","version":"1.0","id":1,"params":[{"status":True}]}
        elif(command=="off"):
            data = {"method":"setPowerStatus","version":"1.0","id":1,"params":[{"status":False}]}
        elif(command=="vol_up"):
            data = {"method":"setAudioVolume","version":"1.0","id":1,"params":[{"target":"speaker","volume":"+1"}]}
            url = "http://192.168.1.168/sony/audio"
        elif(command=="vol_down"):
            data = {"method":"setAudioVolume","version":"1.0","id":1,"params":[{"target":"speaker","volume":"-1"}]}
            url = "http://192.168.1.168/sony/audio"

        data = json.dumps(data)
        _LOGGER.debug("Data being sent: %s", data)
        try:
            _LOGGER.debug("Command: %s", command)
            r = requests.post(url, data=data, headers=DEFAULT_HEADER)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            _LOGGER.warning("Sony Receiver %s refused connection", self._name)
        _LOGGER.debug("Response: %s", r.text)

    def update(self):
        # """Get the latest details from the device."""
        # try:
        #     telnet = telnetlib.Telnet(self._host, self._port, self._timeout)
        # except OSError:
        #     _LOGGER.warning("Sony Receiver %s refused connection", self._name)
        #     return False

        # pwstate = self.telnet_request(telnet, "?P", "PWR")
        # if pwstate:
        #     self._pwstate = pwstate

        # volume_str = self.telnet_request(telnet, "?V", "VOL")
        # self._volume = int(volume_str[3:]) / MAX_VOLUME if volume_str else None

        # muted_value = self.telnet_request(telnet, "?M", "MUT")
        # self._muted = (muted_value == "MUT0") if muted_value else None

        # # Build the source name dictionaries if necessary
        # if not self._source_name_to_number:
        #     for i in range(MAX_SOURCE_NUMBERS):
        #         result = self.telnet_request(telnet, f"?RGB{str(i).zfill(2)}", "RGB")

        #         if not result:
        #             continue

        #         source_name = result[6:]
        #         source_number = str(i).zfill(2)

        #         self._source_name_to_number[source_name] = source_number
        #         self._source_number_to_name[source_number] = source_name

        # source_number = self.telnet_request(telnet, "?F", "FN")

        # if source_number:
        #     self._selected_source = self._source_number_to_name.get(source_number[2:])
        # else:
        #     self._selected_source = None

        # telnet.close()
        return True

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    # @property
    # def state(self):
    #     """Return the state of the device."""
    #     if self._pwstate == "PWR2":
    #         return STATE_OFF
    #     if self._pwstate == "PWR1":
    #         return STATE_OFF
    #     if self._pwstate == "PWR0":
    #         return STATE_ON

    #     return None

    # @property
    # def is_volume_muted(self):
    #     """Boolean if volume is currently muted."""
    #     return self._muted

    # @property
    # def source(self):
    #     """Return the current input source."""
    #     return self._selected_source

    # @property
    # def source_list(self):
    #     """List of available input sources."""
    #     return list(self._source_name_to_number)

    def turn_off(self):
        """Turn off media player."""
        self.send_command("off")

    def volume_up(self):
        """Volume up media player."""
        self.send_command("vol_up")

    def volume_down(self):
        """Volume down media player."""
        self.send_command("vol_down")

    # def mute_volume(self, mute):
    #     """Mute (true) or unmute (false) media player."""
    #     self.telnet_command("MO" if mute else "MF")

    def turn_on(self):
        """Turn the media player on."""
        self.send_command("on")

    # def select_source(self, source):
    #     """Select input source."""
    #     self.telnet_command(f"{self._source_name_to_number.get(source)}FN")