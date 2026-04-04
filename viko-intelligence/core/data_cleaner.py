# core/data_cleaner.py

import pandas as pd
import numpy as np
import re

class DataCleaner:
    """
    Motor de limpieza automatizada de DataFrames.
    Diseñado con operaciones vectorizadas para máxima eficiencia en RAM.
    """

    NULL_THRESHOLD: float = 0.60  # Si una columna tiene > 60% de nulos, se elimina
    CARDINALITY_THRESHOLD: float = 0.50 # Si los valores únicos son < 50%, es categoría

    @staticmethod
    def _standardize_columns(df: pd.DataFrame) -> None:
        """
        Normaliza los nombres de las columnas en el mismo DataFrame (In-Place).
        Ej: ' Precio de Venta ' -> 'precio_de_venta'
        """
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r'\s+', '_', regex=True)
            .str.replace(r'[^a-z0-9_]', '', regex=True)
        )

    @staticmethod
    def _clean_currency_and_numbers(df: pd.DataFrame) -> None:
        """
        Detecta columnas tipo 'object' (strings) que parecen dinero o números con comas,
        y las convierte a floats vectorizadamente.
        """
        for col in df.select_dtypes(include=['object']).columns:
            # Verificamos si al menos un valor de muestra tiene un símbolo de moneda común
            sample = df[col].dropna().head(10).astype(str)
            if sample.str.contains(r'[\$€£]|,\d{3}').any():
                try:
                    # Removemos símbolos de moneda, comas y espacios
                    cleaned_col = df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
                    # Convertimos strings vacíos a NaN para que pd.to_numeric los maneje
                    cleaned_col = cleaned_col.replace('', np.nan)
                    df[col] = pd.to_numeric(cleaned_col)
                except ValueError:
                    continue # Si falla, la dejamos como estaba

    @staticmethod
    def _optimize_dtypes_and_dates(df: pd.DataFrame) -> None:
        """Fuerza la detección de fechas para activar las gráficas."""
        for col in df.columns:
            # Si el nombre de la columna tiene 'date', 'fecha', 'año' o 'month'
            # intentamos convertirla a fecha obligatoriamente.
            col_lower = col.lower()
            if any(word in col_lower for word in ['date', 'fecha', 'year', 'month', 'order']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Optimización de memoria para categorías (mantenemos esto)
            if df[col].dtype == 'object':
                num_unique = df[col].nunique()
                num_total = len(df[col])
                if num_total > 0 and (num_unique / num_total) < 0.5:
                    df[col] = df[col].astype('category')

    @staticmethod
    def _handle_missing_values(df: pd.DataFrame) -> None:
        """
        Aplica estrategias de imputación o eliminación de nulos.
        """
        # 1. Eliminar columnas insalvables (> 60% nulos)
        threshold_count = int((1 - DataCleaner.NULL_THRESHOLD) * len(df))
        df.dropna(axis=1, thresh=threshold_count, inplace=True)

        # 2. Imputar numéricos con la mediana (más robusta ante valores atípicos que la media)
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

        # 3. Imputar categóricos/strings con el valor más frecuente (moda) o 'Desconocido'
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            if df[col].isnull().any():
                if not df[col].mode().empty:
                    # En Pandas, rellenar categóricos requiere manejar las categorías explícitamente a veces,
                    # pero fillna con la moda suele ser seguro en versiones recientes.
                    mode_val = df[col].mode()[0]
                    if df[col].dtype.name == 'category' and mode_val not in df[col].cat.categories:
                        df[col] = df[col].cat.add_categories([mode_val])
                    df[col] = df[col].fillna(mode_val)

    @classmethod
    def clean(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Punto de entrada. Ejecuta el pipeline completo de limpieza.
        Modifica el DataFrame en su mayor parte In-Place para reducir el footprint de RAM.
        
        Args:
            df (pd.DataFrame): DataFrame crudo proveniente de file_validator.py
            
        Returns:
            pd.DataFrame: DataFrame limpio, optimizado y listo para Machine Learning.
        """
        # Trabajamos sobre una copia para evitar el SettingWithCopyWarning, 
        # pero las operaciones internas mutan este nuevo objeto.
        df_clean = df.copy()
        
        cls._standardize_columns(df_clean)
        cls._clean_currency_and_numbers(df_clean)
        cls._optimize_dtypes_and_dates(df_clean)
        cls._handle_missing_values(df_clean)
        
        return df_clean