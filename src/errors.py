"""Ошибки интеграции модулей проекта."""


class IntegrationError(Exception):
    """Базовая ошибка интеграционного слоя."""

    code = "integration_error"


class ModuleUnavailableError(IntegrationError):
    """Файл обмена или связанный модуль недоступен."""

    code = "module_unavailable"


class IntegrationTimeoutError(IntegrationError):
    """Превышено время ожидания файла обмена."""

    code = "timeout"


class InvalidMessageError(IntegrationError):
    """Сообщение не соответствует ожидаемой структуре."""

    code = "invalid_message"


class VersionConflictError(IntegrationError):
    """Версия сообщения несовместима с интеграционным модулем."""

    code = "version_conflict"
