# core/predictor_core.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

class VIKOEngineError(Exception):
    pass

print("🚀 Cargando PredictorCore V4 (Zero-Click BI Auto-Discovery)...")

class PredictorCore:
    MIN_SAMPLES_FOR_ML = 300

    @staticmethod
    def _detect_target_column(df: pd.DataFrame) -> str:
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            raise VIKOEngineError("El archivo no contiene columnas numéricas válidas.")

        keywords = ['venta', 'sale', 'total', 'precio', 'price', 'ingreso', 'revenue', 'importe', 'monto']
        for col in numeric_cols:
            if any(kw in col.lower() for kw in keywords):
                return col

        best_col = numeric_cols[0]
        max_sum = df[best_col].sum()
        for col in numeric_cols[1:]:
            col_sum = df[col].sum()
            if col_sum > max_sum:
                max_sum = col_sum
                best_col = col

        return best_col

    @staticmethod
    def _extract_business_insights(df: pd.DataFrame, target_col: str) -> dict:
        insights = {
            "kpis": {
                "total_valor": float(df[target_col].sum()),
                "promedio_transaccion": float(df[target_col].mean()),
                "total_operaciones": int(len(df)),
            },
            "charts": {
                "top_categories": {},
                "time_trend": []
            }
        }

        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            date_col = date_cols[0]
            try:
                trend = df.groupby(pd.Grouper(key=date_col, freq='ME'))[target_col].sum().reset_index()
                insights["charts"]["time_trend"] = [
                    {"fecha": row[date_col].strftime('%Y-%m'), "valor": float(row[target_col])}
                    for _, row in trend.iterrows()
                ]
            except Exception as e:
                print(f"⚠️ Error agrupando fechas: {e}")

        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            main_cat_col = cat_cols[0] 
            top_5 = df.groupby(main_cat_col)[target_col].sum().sort_values(ascending=False).head(5)
            insights["charts"]["top_categories"] = top_5.to_dict()

        return insights

    @staticmethod
    def _feature_engineering(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        df_ml = df.copy()
        
        date_cols = df_ml.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            date_col = date_cols[0]
            df_ml['mes'] = df_ml[date_col].dt.month
            df_ml['dia_semana'] = df_ml[date_col].dt.dayofweek
            df_ml['es_fin_semana'] = df_ml['dia_semana'].apply(lambda x: 1 if x >= 5 else 0)
            df_ml = df_ml.drop(columns=list(date_cols))

        cat_cols = df_ml.select_dtypes(include=['object', 'category']).columns
        cat_cols_to_encode = [col for col in cat_cols if df_ml[col].nunique() <= 10]
        if cat_cols_to_encode:
            df_ml = pd.get_dummies(df_ml, columns=cat_cols_to_encode, drop_first=True, dtype=int)
            
        df_ml = df_ml.select_dtypes(include=['number', 'bool']).fillna(0)
        return df_ml

    @staticmethod
    def _train_and_predict(df: pd.DataFrame, target_col: str) -> dict:
        df_processed = PredictorCore._feature_engineering(df, target_col)
        X = df_processed.drop(columns=[target_col], errors='ignore')
        y = df_processed[target_col]

        if X.empty:
            return {"metrics": {}}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=50, max_depth=15, random_state=42)
        model.fit(X_train, y_train)

        future_X = pd.DataFrame([X.mean()], columns=X.columns)
        future_pred = model.predict(future_X)[0]

        return {
            "metrics": {
                "prediccion_tendencia_futura": float(future_pred),
            }
        }

    @classmethod
    def analyze_dataset(cls, df: pd.DataFrame) -> dict:
        target_col = cls._detect_target_column(df)
        print(f"🎯 Auto-descubrimiento: {target_col}")

        biz_data = cls._extract_business_insights(df, target_col)
        
        if len(df) >= cls.MIN_SAMPLES_FOR_ML:
            ml_results = cls._train_and_predict(df, target_col)
            return {
                "status": "machine_learning_success",
                "message": f"Análisis predictivo completado para '{target_col}'.",
                "metrics": {**biz_data["kpis"], **ml_results["metrics"]},
                "charts": biz_data["charts"],
                "target_column": target_col
            }
        else:
            return {
                "status": "descriptive_only",
                "message": f"Análisis descriptivo completado para '{target_col}'.",
                "metrics": biz_data["kpis"],
                "charts": biz_data["charts"],
                "target_column": target_col
            }