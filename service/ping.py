import asyncio

import httpx
from fastapi import FastAPI

from config import DICT_OF_SERVICES, ServiceEnum


async def ping(prefix: str, client: httpx.AsyncClient) -> None:
    try:
        response = await client.get("http://local-service/ping", timeout=2.0)
        status = (
            ServiceEnum.healthy if response.status_code == 200 else ServiceEnum.dead
        )

    except httpx.RequestError:
        status = ServiceEnum.dead

    service = DICT_OF_SERVICES[prefix]

    if service.status < ServiceEnum.maintenance:
        service.status = status


async def ping_all(app: FastAPI) -> None:
    clients: dict[str, httpx.AsyncClient] = app.state.proxy_clients

    await asyncio.gather(
        *(
            ping(prefix, client)
            for prefix, client in clients.items()
            if DICT_OF_SERVICES[prefix].status < ServiceEnum.maintenance
        )
    )


async def heartbeat(app: FastAPI) -> None:
    while True:
        await ping_all(app)
        await asyncio.sleep(10)
