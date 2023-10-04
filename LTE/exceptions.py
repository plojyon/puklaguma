class UnexpectedResponse(Exception):
    pass


class HealthCheckException(Exception):
    pass


class DeadModuleException(HealthCheckException):
    pass


class NoSignalException(HealthCheckException):
    pass


class PinRequired(HealthCheckException):
    pass


class NetworkRegistrationException(HealthCheckException):
    pass


class NetworkOperatorException(HealthCheckException):
    pass


class MemoryStorageException(HealthCheckException):
    pass
