from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from template_env import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {})
