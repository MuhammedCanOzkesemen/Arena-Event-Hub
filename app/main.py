from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.routers.api_events import router as api_events_router
from app.routers.html_routes import router as html_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Sports event calendar backend challenge project.",
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(api_events_router)
    app.include_router(html_router)

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
