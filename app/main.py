from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.web.support import router as support_app_router

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(support_app_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
