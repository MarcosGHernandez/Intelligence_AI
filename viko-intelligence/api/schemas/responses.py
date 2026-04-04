# api/schemas/responses.py
from pydantic import BaseModel
from typing import Dict, Any, List

class AnalysisResponse(BaseModel):
    status: str
    message: str
    metrics: Dict[str, Any]  # Aquí irán 'total_valor', etc.
    charts: Dict[str, Any]   # Aquí irá 'time_trend'
    filename: str
    target_column: str