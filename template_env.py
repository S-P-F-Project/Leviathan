import os
from pathlib import Path

from fastapi.templating import Jinja2Templates

from config import (
    ABOUT_TEXT,
    OFFER_URL,
    PLAYER_URL,
    RULES_URL,
    SELLER,
    SHOP_URL,
    SITE_NAME,
    WIKI_URL,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals.update(
    site_name=SITE_NAME,
    shop_url=SHOP_URL,
    player_url=PLAYER_URL,
    wiki_url=WIKI_URL,
    offer_url=OFFER_URL,
    rules_url=RULES_URL,
    about_text=ABOUT_TEXT,
    seller=SELLER,
)

LOCAL_RUN = os.getenv("FASTAPISTATIC") == "1"


def static_url(file: str) -> str:
    static_path = STATIC_DIR / file
    v = int(static_path.stat().st_mtime) if static_path.exists() else 0

    if LOCAL_RUN:
        return f"/static/{file}?v={v}"

    return f"/leviathan/static/{file}?v={v}"


templates.env.filters["ver"] = static_url
