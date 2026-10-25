import asyncio

from config import (
    DICT_OF_SERVICES,
    LOCAL_RUN,
    SERVICE_DIR,
    SOCKET_DIR,
    Service,
    ServiceEnum,
)

from .command import run

SYSTEMD_ARGS = ("--user",)


def unit_name(name: str) -> str:
    return f"spf-{name.lstrip('/')}.service"


async def start_service(name: str, service: Service) -> None:
    destination = SERVICE_DIR / name.lstrip("/")

    await run(
        "systemd-run",
        *SYSTEMD_ARGS,
        f"--unit={unit_name(name)}",
        "--collect",
        f"--setenv=FASTAPISTATIC={LOCAL_RUN:d}",
        f"--setenv=FASTAPISTATIC_LEV={LOCAL_RUN:d}",
        "--property=Type=exec",
        "--property=Restart=on-failure",
        "--property=RestartSec=3s",
        f"--property=WorkingDirectory={destination}",
        str(destination / ".venv/bin/python"),
        "-m",
        "uvicorn",
        "app:app",
        "--uds",
        service.socket,
    )

    service.status = ServiceEnum.dead


async def stop_service(name: str) -> None:
    unit = unit_name(name)

    state = await run(
        "systemctl",
        *SYSTEMD_ARGS,
        "show",
        "--property=LoadState",
        "--value",
        unit,
    )

    if state == "not-found":
        return

    await run("systemctl", *SYSTEMD_ARGS, "stop", unit)


async def start_all_services() -> None:
    SOCKET_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)

    results = await asyncio.gather(
        *(start_service(name, service) for name, service in DICT_OF_SERVICES.items()),
        return_exceptions=True,
    )

    errors = [
        f"{name}: {result}"
        for name, result in zip(DICT_OF_SERVICES, results)
        if isinstance(result, Exception)
    ]

    if errors:
        raise RuntimeError("Service startup failed:\n" + "\n".join(errors))


async def stop_all_services() -> None:
    results = await asyncio.gather(
        *(stop_service(name) for name in DICT_OF_SERVICES),
        return_exceptions=True,
    )

    errors = [
        f"{name}: {result}"
        for name, result in zip(DICT_OF_SERVICES, results)
        if isinstance(result, Exception)
    ]

    if errors:
        raise RuntimeError("Service shutdown failed:\n" + "\n".join(errors))
