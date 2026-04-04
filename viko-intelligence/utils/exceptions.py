# utils/exceptions.py

class VIKOEngineError(Exception):
    """Clase base para las excepciones del motor VIKO-Intelligence."""
    pass

class FileValidationError(VIKOEngineError):
    """Excepción lanzada cuando un archivo no cumple los criterios de seguridad o formato."""
    pass