import logging
import time

import serial

from LTE.exceptions import *

logger = logging.getLogger("SMS")
logger.setLevel(logging.INFO)

ser = serial.Serial("/dev/ttyS0", 115200)
ser.flushInput()

POWER_PIN = 6

ALLOW_ROAMING = True


def send_at(command, back, timeout, raw=False):
    """Send raw AT command and parse response."""
    command_repr = str(command)
    if raw:
        ser.write(command)
        command = command.decode()
    else:
        ser.write((command + "\r\n").encode())

    time.sleep(timeout)

    if ser.inWaiting():
        rec_buff = ser.read(ser.inWaiting())
    else:
        rec_buff = b""

    try:
        response = rec_buff.decode().replace(command, "").strip()
    except UnicodeDecodeError:
        # Sometimes the response is not decoded properly. But it still tends to work.
        logger.warning(f"Failed to decode response: {rec_buff}")
        return rec_buff

    response_repr = response.replace("\r\n", "\\n")
    log_msg = f"{command_repr.strip()} returned {response_repr}"
    if back not in response:
        raise UnexpectedResponse(f"{log_msg} (expected {back})")

    logger.debug(f"OK: {log_msg}")
    return response.split("\r\n")[0]


class NetworkStatus:
    NOT_REGISTERED = 0
    REGISTERED = 1
    SEARCHING = 2
    DENIED = 3
    UNKNOWN = 4
    ROAMING = 5

    @staticmethod
    def name(code):
        return [
            "Not registered",
            "Registered",
            "Searching",
            "Denied",
            "Unknown",
            "Roaming",
        ][code]
