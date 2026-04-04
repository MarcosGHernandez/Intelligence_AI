# core/file_validator.py

import io
import os
import pandas as pd
from typing import Set

# Importamos la excepción personalizada que definimos en utils
from utils.exceptions import FileValidationError

class FileValidator:
    """
    Clase encargada de la validación estricta y carga segura de archivos.
    Garantiza que solo formatos permitidos y tamaños manejables ingresen al motor.
    """
    
    MAX_SIZE_MB: int = 5
    MAX_SIZE_BYTES: int = MAX_SIZE_MB * 1024 * 1024
    
    ALLOWED_EXTENSIONS: Set[str] = {'.csv', '.xlsx', '.xls'}
    ALLOWED_MIME_TYPES: Set[str] = {
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    }

    @staticmethod
    def _validate_extension(filename: str) -> None:
        """Verifica que la extensión del archivo esté en la whitelist."""
        _, ext = os.path.splitext(filename)
        if ext.lower() not in FileValidator.ALLOWED_EXTENSIONS:
            raise FileValidationError(f"Extensión '{ext}' no soportada. Formatos válidos: CSV, Excel.")

    @staticmethod
    def _validate_mime_type(mime_type: str) -> None:
        """Verifica que el MIME type coincida con los formatos esperados por seguridad."""
        if mime_type not in FileValidator.ALLOWED_MIME_TYPES:
            raise FileValidationError(f"Tipo MIME '{mime_type}' bloqueado por políticas de seguridad.")

    @staticmethod
    def _validate_size(file_content: bytes) -> None:
        """Asegura que el archivo no exceda el límite de memoria para entornos Serverless."""
        if len(file_content) > FileValidator.MAX_SIZE_BYTES:
            raise FileValidationError(f"El archivo excede el límite máximo de {FileValidator.MAX_SIZE_MB}MB.")

    @classmethod
    def load_and_validate(cls, filename: str, mime_type: str, file_content: bytes) -> pd.DataFrame:
        """
        Punto de entrada principal. Ejecuta las validaciones de seguridad y 
        transforma los bytes en un DataFrame de Pandas en memoria.
        
        Args:
            filename (str): Nombre original del archivo.
            mime_type (str): Tipo MIME reportado por el cliente.
            file_content (bytes): Contenido del archivo en bytes puros.
            
        Returns:
            pd.DataFrame: Estructura de datos lista para el módulo de limpieza.
            
        Raises:
            FileValidationError: Si alguna validación de seguridad falla o el archivo está corrupto.
        """
        # 1. Ejecutar cadena de validaciones de seguridad
        cls._validate_extension(filename)
        cls._validate_mime_type(mime_type)
        cls._validate_size(file_content)

        # 2. Cargar en memoria de forma segura
        file_buffer = io.BytesIO(file_content)
        
        try:
            if filename.lower().endswith('.csv'):
                # engine='c' es más rápido y eficiente en memoria para CSVs
                df = pd.read_csv(file_buffer, engine='c', on_bad_lines='skip')
            else:
                # Carga de Excel (requerirá la librería openpyxl en requirements.txt)
                df = pd.read_excel(file_buffer)
                
            if df.empty:
                raise FileValidationError("El archivo fue procesado correctamente, pero no contiene datos.")
                
            return df
            
        except Exception as e:
            # Capturamos errores de Pandas (ej. CSV malformado) y los estandarizamos
            raise FileValidationError(f"Error interno al decodificar el archivo: {str(e)}")