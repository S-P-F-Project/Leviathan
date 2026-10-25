from fastapi.templating import Jinja2Templates

from config import ABOUT_TEXT, BASE_DIR, LOCAL_RUN, SELLER, STATIC_DIR


def static_url(file: str) -> str:
    static_path = STATIC_DIR / file
    v = int(static_path.stat().st_mtime) if static_path.exists() else 0

    if LOCAL_RUN:
        return f"/static/{file}?v={v}"

    return f"/leviathan/static/{file}?v={v}"


templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

templates.env.filters["ver"] = static_url

templates.env.globals.update(about_text=ABOUT_TEXT, seller=SELLER)
