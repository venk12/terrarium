import time
import network
import umqtt.simple as simple
import wifi_setup
import machine
from utils import log_error, offline_log_error, debug_print, resolve_mdns_hostname
import os
import ujson
import json
from actuator_specific_folder.pumps import turn_off, turn_on