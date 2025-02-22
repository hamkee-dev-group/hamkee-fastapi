from fastapi import FastAPI
from services import settings, logger
from api.urls import router as api_router


def get_application() -> FastAPI:
    """Return FastAPI application."""

    application = FastAPI(
        debug=settings.DEBUG,
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
    )
    application.include_router(api_router, prefix=settings.API_PREFIX)

    return application


app = get_application()


if settings.CORS_ALLOW_ALL_ORIGINS:
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS allowed for all origins.")
else:
    logger.info("CORS not allowed for all origins.")
