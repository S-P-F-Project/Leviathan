# Знаете я всей душой не люблю такого типа конфиги. Чистый голый py файл
# Но мне так похуй и влом делать json или подобное, а этот сервис
# будет перезапускаться раз в никогда что мне посто влом делать что-то адекватное

import os
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SERVICE_DIR = BASE_DIR / ".runtime"
STATIC_DIR = BASE_DIR / "static"

SOCKET_DIR = Path(os.environ["XDG_RUNTIME_DIR"]) / "spf"

LOCAL_RUN = os.getenv("FASTAPISTATIC") == "1"

ABOUT_TEXT = """\
Потом дописать.
"""

SELLER = {
    "full_name": "stub",
    "inn": "stub",
    "email": "stub",
    "phone": "+ stub",
}


class ServiceEnum(IntEnum):
    healthy = 0
    dead = 1

    setup = 2
    maintenance = 3


@dataclass
class Service:
    url: str

    is_public: bool
    socket: str
    public_prefix: str | None

    status: ServiceEnum = ServiceEnum.setup


DICT_OF_SERVICES = {
    "/wiki": Service(
        "https://github.com/S-P-F-Project/wiki.git",
        True,
        str(SOCKET_DIR / "wiki.sock"),
        "/wiki",
    ),
}
