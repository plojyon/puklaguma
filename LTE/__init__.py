import time

import RPi.GPIO as GPIO
import serial

from LTE.exceptions import *
from LTE.health_check import health_check
from LTE.utils import *


def send_sms(phone_number, text_message):
    """Send an SMS to a phone number."""
    # Set sms mode to text
    send_at("AT+CMGF=1", "OK", 1)
    # Send short message
    send_at('AT+CMGS="' + phone_number + '"', ">", 2)
    ser.write(text_message.encode())
    send_at(b"\x1A", "OK", 20, raw=True)


def receive_sms():
    # Set sms mode to text
    send_at("AT+CMGF=1", "OK", 1)
    # Set sms storage to SIM
    send_at('AT+CPMS="SM","SM","SM"', "OK", 1)
    # Read message
    send_at("AT+CMGR=1", "+CMGR:", 2)
    if "OK" in rec_buff:
        print(rec_buff)


def power_on():
    """Power on the LTE module."""
    logger.info("LTE initialization started")
    initialize_power_pin()
    GPIO.output(POWER_PIN, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(POWER_PIN, GPIO.LOW)
    time.sleep(20)
    ser.flushInput()
    logger.info("LTE is ready")


def power_off():
    """Power off the LTE module."""
    logger.info("LTE is loging off")
    initialize_power_pin()
    GPIO.output(POWER_PIN, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(POWER_PIN, GPIO.LOW)
    time.sleep(18)

    if ser != None:
        ser.close()
    GPIO.cleanup()

    logger.info("eepy -__-")


def unlock_pin(pin):
    """Unlock the SIM card with the given PIN."""
    if isinstance(pin, int):
        pin = str(pin)
    elif len(pin) == 2:
        pin = f"{pin[0]},{pin[1]}"

    try:
        response = send_at(f"AT+CPIN={pin}", "OK", 1)
    except UnexpectedResponse as e:
        raise PinRequired(f"Failed to unlock SIM card") from e
    logger.info("SIM card unlocked successfully")


def initialize_power_pin():
    """Initialize the GPIO pin for module power."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(POWER_PIN, GPIO.OUT)
    time.sleep(0.1)
