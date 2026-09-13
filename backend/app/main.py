import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import router as api_router
from app.db.database import engine

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title="Lenny Growth Assistant",
    description="Phase 1 API foundation for the Lenny Growth Assistant.",
    version="0.1.0",
    lifespan=lifespan,
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "lenny-growth-assistant", "status": "ok"}


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return HealthResponse(
            status="ok",
            service="lenny-growth-assistant",
            database="connected",
        )
    except SQLAlchemyError:
        return HealthResponse(
            status="degraded",
            service="lenny-growth-assistant",
            database="unavailable",
        )
