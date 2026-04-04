# api/main.py
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# Importaciones de tu motor - Asegúrate de que las rutas sean correctas
try:
    from core.data_cleaner import DataCleaner
    from core.file_validator import FileValidator
    from core.predictor_core import PredictorCore
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    # Si falla la ruta, intenta con importación relativa según tu estructura
    from .core.data_cleaner import DataCleaner
    from .core.file_validator import FileValidator
    from .core.predictor_core import PredictorCore

app = FastAPI(title="VIKO-Intelligence API V4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResponse(BaseModel):
    status: str
    message: str
    metrics: Dict[str, Any]
    charts: Dict[str, Any]
    filename: str
    target_column: str

@app.get("/test")
async def test_connection():
    return {"status": "VIVO", "engine": "VIKO-Intelligence V4"}

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_file(file: UploadFile = File(...)):
    print(f"📥 [VIKOTECH] Procesando: {file.filename}")
    try:
        content = await file.read()
        df_raw = FileValidator.load_and_validate(
            filename=file.filename,
            mime_type=file.content_type,
            file_content=content
        )
        df_clean = DataCleaner.clean(df_raw)
        results = PredictorCore.analyze_dataset(df_clean)
        
        return AnalysisResponse(
            status=results["status"],
            message=results["message"],
            metrics=results["metrics"],
            charts=results.get("charts", {}),
            filename=file.filename,
            target_column=results["target_column"]
        )
    except Exception as e:
        print(f"❌ [ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ESTO ES LO QUE FALTA PARA QUE ARRANQUE EL SERVIDOR ---
if __name__ == "__main__":
    print("🔧 Iniciando servidor Uvicorn...")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)