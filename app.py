import asyncio
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from router.index import router as index_router
from router.proxy import init_proxy
from router.proxy import router as proxy_router
from service.deploy import deploy_all_services
from service.ping import heartbeat
from service.systemd import start_all_services, stop_all_services
from template_env import LOCAL_RUN


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with AsyncExitStack() as stack:
        # боже прости меня но мне прийдётся включить режим gpt иначе через месяц я забуду что за хуйня

        # Сетапим stop_all_services. Добавляем его в выход стака и за одно
        # убивает все сервисы если кто-то ещё жив как-то.
        stack.push_async_callback(stop_all_services)
        await stop_all_services()

        # Деплоим все сервисы
        await deploy_all_services()

        # Стартуем systemd
        await start_all_services()

        # Поднимаем клиенты
        await init_proxy(app, stack)

        # Поднимаем проверку сервисов. Без клиентов эта хуйня грохнется.
        task = asyncio.create_task(heartbeat(app))

        try:
            yield

        finally:
            task.cancel()
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

app.include_router(index_router)
app.include_router(proxy_router)
