import os
from datetime import date
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from config import (
    AGE_COOKIE_NAME,
    AGE_LIMIT,
    CONTACTS,
    MICROSERVICES,
    OFFER_URL,
    REQUISITES,
    SITE_DESCRIPTION,
    SITE_NAME,
    SITE_TAGLINE,
    WIKI_URL,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def is_guest(request: Request) -> bool:
    # Future auth integrations may populate request.scope["user"].
    user = request.scope.get("user")
    return not getattr(user, "is_authenticated", False)


def needs_age_confirmation(request: Request) -> bool:
    return is_guest(request) and request.cookies.get(AGE_COOKIE_NAME) != str(AGE_LIMIT)


templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals.update(
    site_name=SITE_NAME,
    site_tagline=SITE_TAGLINE,
    site_description=SITE_DESCRIPTION,
    wiki_url=WIKI_URL,
    offer_url=OFFER_URL,
    contacts=CONTACTS,
    requisites=REQUISITES,
    microservices=MICROSERVICES,
    age_limit=AGE_LIMIT,
    age_cookie_name=AGE_COOKIE_NAME,
    is_guest=is_guest,
    needs_age_confirmation=needs_age_confirmation,
    current_year=date.today().year,
)

# Keep the original reverse-proxy deployment behavior.
LOCAL_RUN = os.getenv("FASTAPISTATIC") == "1"


def static_url(file: str) -> str:
    static_path = STATIC_DIR / file
    version = int(static_path.stat().st_mtime) if static_path.is_file() else 0
    prefix = "/static" if LOCAL_RUN else "/leviathan/static"
    return f"{prefix}/{file}?v={version}"


templates.env.filters["ver"] = static_url
