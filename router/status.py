from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from config import DICT_OF_SERVICES, SELLER, ServiceEnum
from template_env import templates

router = APIRouter()

STATUS_TEXT = {
    ServiceEnum.healthy: "Работает",
    ServiceEnum.dead: "Недоступен",
    ServiceEnum.maintenance: "Технические работы",
    ServiceEnum.setup: "Запускается",
}


@router.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    services = [
        {
            "name": service.name,
            "state": service.status.name,
            "label": STATUS_TEXT[service.status],
        }
        for name, service in DICT_OF_SERVICES.items()
    ]

    healthy_count = sum(
        service.status == ServiceEnum.healthy for service in DICT_OF_SERVICES.values()
    )

    return templates.TemplateResponse(
        request,
        "status.html",
        {
            "services": services,
            "healthy_count": healthy_count,
            "seller": SELLER,
        },
    )
