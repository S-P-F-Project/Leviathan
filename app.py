from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from router.index import router as index_router
from router.status import router as status_router
from template_env import LOCAL_RUN, STATIC_DIR

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(index_router)
app.include_router(status_router)

if LOCAL_RUN:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
