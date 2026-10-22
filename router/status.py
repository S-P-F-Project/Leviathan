from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from template_env import templates

router = APIRouter()


@router.get("/status/", response_class=HTMLResponse)
async def status_page(request: Request):
    return templates.TemplateResponse(request, "status.html", {})
