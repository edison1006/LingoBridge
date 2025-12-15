from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import grammar


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Init DB / Redis connections here if needed
    yield
    # TODO: Close connections here


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(grammar.router, prefix="/api/grammar", tags=["grammar"])


