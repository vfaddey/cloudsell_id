from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
from src.core.config import settings

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/",
    title=settings.APP_NAME
)
app.include_router(auth_router)
app.include_router(users_router)


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)