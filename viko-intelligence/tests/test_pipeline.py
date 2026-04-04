# tests/test_pipeline.py

import os
import pandas as pd
import numpy as np

# Importamos nuestros módulos del Core
from core.file_validator import FileValidator
from core.data_cleaner import DataCleaner
from core.predictor_core import PredictorCore

def generar_dataset_prueba(filename="ventas_pos_dummy.csv"):
    """Genera un dataset sintético de ventas de inventario con ruido e inconsistencias intencionales."""
    print("⏳ Generando dataset sintético de prueba...")
    np.random.seed(42)
    n_rows = 400  # Forzamos más de 300 para activar el ML

    data = {
        ' Fecha de Venta ': pd.date_range(start='2025-01-01', periods=n_rows, freq='D').astype(str),
        'Producto_ID': np.random.choice(['PROD_01', 'PROD_02', 'PROD_03'], n_rows),
        'Precio Venta': ['$' + str(np.round(np.random.uniform(10, 100), 2)) for _ in range(n_rows)], # Formato moneda sucio
        'Cantidad_Vendida': np.random.poisson(lam=15, size=n_rows), # Nuestra variable a predecir
        'Categoria_Extra': np.random.choice(['A', 'B', np.nan], n_rows) # Nulos intencionales
    }
    
    df = pd.DataFrame(data)
    # Introducir algunos nulos aleatorios en el precio para probar el DataCleaner
    df.loc[10:20, 'Precio Venta'] = np.nan 
    
    # Guardamos el CSV
    df.to_csv(filename, index=False)
    print(f"✅ Archivo '{filename}' creado con {n_rows} registros.\n")
    return filename

def ejecutar_pipeline():
    filename = generar_dataset_prueba()
    
    try:
        # --- FASE 1: INGESTA Y VALIDACIÓN ---
        print("🚀 INICIANDO FASE 1: VALIDACIÓN")
        with open(filename, "rb") as f:
            file_content = f.read()
            
        # Simulamos los datos que llegarían de FastAPI
        df_raw = FileValidator.load_and_validate(
            filename=filename, 
            mime_type="text/csv", 
            file_content=file_content
        )
        print("✅ Validación exitosa. DataFrame crudo cargado en memoria.")
        print(f"   Formato inicial de columnas: {list(df_raw.columns)}\n")

        # --- FASE 2: LIMPIEZA AUTOMÁTICA ---
        print("🧹 INICIANDO FASE 2: DATA CLEANER")
        df_clean = DataCleaner.clean(df_raw)
        print("✅ Limpieza completada.")
        print(f"   Columnas estandarizadas: {list(df_clean.columns)}")
        print(f"   Tipos de datos optimizados:\n{df_clean.dtypes}\n")

        # --- FASE 3: MACHINE LEARNING ---
        print("🧠 INICIANDO FASE 3: PREDICTOR CORE")
        # El DataCleaner convirtió 'Cantidad_Vendida' a 'cantidad_vendida'
        target = 'cantidad_vendida' 
        
        resultado = PredictorCore.analyze_target(df_clean, target_col=target)
        
        print(f"✅ Análisis completado. Estado: {resultado['status']}")
        print(f"   Mensaje: {resultado['message']}")
        print("   Métricas:")
        for k, v in resultado['metrics'].items():
            print(f"      - {k}: {v}")

    except Exception as e:
        print(f"\n❌ ERROR EN EL PIPELINE: {str(e)}")
        
    finally:
        # Limpieza del archivo temporal
        if os.path.exists(filename):
            os.remove(filename)
            print("\n🗑️ Archivo temporal de prueba eliminado.")

if __name__ == "__main__":
    ejecutar_pipeline()