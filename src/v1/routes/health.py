from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """Проверить работоспособность сервера"""
    return {"status": "healthy"}
