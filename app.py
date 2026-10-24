from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from router.index import router as index_router
from router.proxy import lifespan
from router.proxy import router as proxy_router
from template_env import LOCAL_RUN

app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

if LOCAL_RUN:
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )

app.include_router(index_router)
app.include_router(proxy_router)
