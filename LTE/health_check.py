from LTE.exceptions import *
from LTE.utils import *


def check_echo():
    try:
        send_at("AT", "OK", 1)
    except UnexpectedResponse as e:
        raise DeadModuleException("LTE module not responding") from e


def check_pin():
    try:
        send_at("AT+CPIN?", "+CPIN: READY", 1)
    except UnexpectedResponse as e:
        raise PinRequired("SIM card is locked with a PIN") from e


def check_signal():
    at_response = send_at("AT+CSQ", "OK", 1)
    if at_response == "+CSQ: 99,99":
        raise NoSignalException("Signal known or not detectable")

    # Received Signal Strength Indication and Bit Error Rate
    rssi, ber = at_response.split(": ")[1].split(",")
    return rssi, ber


def check_network():
    try:
        at_response = send_at("AT+CREG?", "OK", 1)
    except UnexpectedResponse as e:
        raise NetworkRegistrationException("Not registered to network") from e
    code = int(at_response.split(",")[1])
    status = NetworkStatus.name(code)
    if not ALLOW_ROAMING and code == NetworkStatus.ROAMING:
        raise NetworkRegistrationException("Roaming is not allowed")
    if code not in [NetworkStatus.REGISTERED, NetworkStatus.ROAMING]:
        raise NetworkRegistrationException(
            f"Not registered to network ({code}: {status})"
        )

    return code, status


def check_operator():
    try:
        at_response = send_at("AT+COPS?", "OK", 1)
    except UnexpectedResponse as e:
        raise NetworkOperatorException("Network operator not found") from e
    splits = at_response.split(": ")[1].split(",")
    return splits[2].strip('"')


def check_storage():
    try:
        at_response = send_at("AT+CPMS?", "OK", 1)
    except UnexpectedResponse as e:
        raise MemoryStorageException("Memory storage not found") from e

    splits = at_response.split(": ")[1].split(",")

    devices = [
        {
            "name": splits[3 * i],
            "used": int(splits[3 * i + 1]),
            "total": int(splits[3 * i + 2]),
        }
        for i in range(len(splits) // 3)
    ]

    usage_str = "; ".join(
        [f"{device['name']}:{device['used']}/{device['total']}" for device in devices]
    )

    if any([device["used"] >= device["total"] for device in devices]):
        raise MemoryStorageException("Memory storage is full")
    return devices, usage_str


def health_check():
    """Assert that the LTE module is fully functional."""
    check_echo()

    check_pin()

    quality = check_signal()
    logger.info(f"Signal quality: {quality}")

    code, status = check_network()
    logger.info(f"Network registration status: {status} ({code})")

    operator = check_operator()
    logger.info(f"Network operator: {operator}")

    devices, usage_str = check_storage()
    logger.info(f"Memory storage: {usage_str}")

    logger.info("Health check passed")
