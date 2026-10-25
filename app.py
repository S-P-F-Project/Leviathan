import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from router.index import router as index_router
from router.proxy import init_proxy
from router.proxy import router as proxy_router
from router.status import router as status_router
from service.deploy import deploy_all_services
from service.ping import heartbeat
from service.systemd import start_all_services, stop_all_services
from template_env import LOCAL_RUN

logger = logging.getLogger("uvicorn.error")


async def prepare_services() -> None:
    try:
        logger.info("Stopping existing services")
        await stop_all_services()

        logger.info("Deploying services")
        await deploy_all_services()

        logger.info("Starting services")
        await start_all_services()

        logger.info("Service initialization completed")

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.exception("Service initialization failed")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with AsyncExitStack() as stack:
        stack.push_async_callback(stop_all_services)

        await init_proxy(app, stack)

        deploy_task = asyncio.create_task(prepare_services())
        heartbeat_task = asyncio.create_task(heartbeat(app))

        try:
            yield

        finally:
            heartbeat_task.cancel()
            deploy_task.cancel()

            for task in (heartbeat_task, deploy_task):
                with suppress(asyncio.CancelledError):
                    await task


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

for router in [
    index_router,
    status_router,
    proxy_router,
]:
    app.include_router(router)
