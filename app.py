import contextlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from router.index import router as index_router
from template_env import LOCAL_RUN


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


app.include_router(index_router)


if LOCAL_RUN:
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )
