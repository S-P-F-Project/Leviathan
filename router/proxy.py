from contextlib import AsyncExitStack
from http.cookiejar import CookieJar, DefaultCookiePolicy
from urllib.parse import quote

import httpx
from anyio import CancelScope
from fastapi import APIRouter, FastAPI, Request
from starlette.responses import PlainTextResponse, Response, StreamingResponse
from starlette.types import Receive, Scope, Send

from config import DICT_OF_SERVICES

router = APIRouter()

METHODS = ["GET", "POST", "HEAD", "OPTIONS"]

HOP_HEADERS = {
    b"connection",
    b"keep-alive",
    b"proxy-connection",
    b"proxy-authenticate",
    b"proxy-authorization",
    b"te",
    b"trailer",
    b"transfer-encoding",
    b"upgrade",
}

TIMEOUT = httpx.Timeout(connect=3.0, read=60.0, write=60.0, pool=5.0)
LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)


class NoStoredCookies(DefaultCookiePolicy):
    def set_ok(self, cookie, request) -> bool:
        return False


async def init_proxy(app: FastAPI, stack: AsyncExitStack) -> None:
    clients: dict[str, httpx.AsyncClient] = {}

    for name, service in DICT_OF_SERVICES.items():
        client = httpx.AsyncClient(
            transport=httpx.AsyncHTTPTransport(uds=service.socket, limits=LIMITS),
            timeout=TIMEOUT,
            follow_redirects=False,
            trust_env=False,
            cookies=CookieJar(policy=NoStoredCookies()),
        )

        clients[name] = await stack.enter_async_context(client)

    app.state.proxy_clients = clients


def filter_headers(headers: list[tuple[bytes, bytes]]) -> list[tuple[bytes, bytes]]:
    blocked = HOP_HEADERS.copy()

    for name, value in headers:
        if name.lower() == b"connection":
            blocked.update(part.strip().lower() for part in value.split(b","))

    return [
        (name.lower(), value) for name, value in headers if name.lower() not in blocked
    ]


def get_raw_path(request: Request) -> bytes:
    raw_path = request.scope.get("raw_path")

    if raw_path is not None:
        return raw_path

    return quote(request.scope["path"], safe="/:@!$&'()*+,;=-._~").encode("ascii")


def find_route(path: str) -> str:
    return "/" + path.lstrip("/").split("/", 1)[0]


class ProxyResponse(StreamingResponse):
    def __init__(self, upstream: httpx.Response) -> None:
        self.upstream = upstream

        super().__init__(upstream.aiter_raw(), status_code=upstream.status_code)

        self.raw_headers = filter_headers(upstream.headers.raw)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await super().__call__(scope, receive, send)

        finally:
            with CancelScope(shield=True):
                await self.upstream.aclose()


@router.api_route("/{path:path}", methods=METHODS)
async def proxy(request: Request) -> Response:
    path = get_raw_path(request)
    prefix = find_route(request.scope["path"])

    service = DICT_OF_SERVICES.get(prefix)

    if service is None or not service.is_public:
        return PlainTextResponse("Not Found", status_code=404)

    if service.status > 0:
        return PlainTextResponse("Service Unavailable", status_code=503)

    query = request.scope.get("query_string", b"")
    target = path + b"?" + query if query else path

    client: httpx.AsyncClient = request.app.state.proxy_clients[prefix]
    outgoing = client.build_request(
        method=request.method,
        url="http://local-service",
        headers=filter_headers(request.headers.raw),
        content=request.stream(),
        extensions={"target": target},  # Orig request without HTTPX URL normalization
    )

    try:
        upstream = await client.send(outgoing, stream=True)

    except httpx.TimeoutException:
        return PlainTextResponse(
            "Gateway Timeout", status_code=504
        )  # TODO: Сделать отдачу нормальной страницы ошибки (в принципе все перехватывать и транслитить в html?)

    except httpx.RequestError:
        return PlainTextResponse("Bad Gateway", status_code=502)

    return ProxyResponse(upstream)
