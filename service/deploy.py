import asyncio
import sys

from config import DICT_OF_SERVICES, SERVICE_DIR

from .command import run


# region git
async def sync_service(name: str, url: str) -> None:
    destination = SERVICE_DIR / name.lstrip("/")

    if not destination.exists():
        await run("git", "clone", "--branch", "master", url, str(destination))
        return

    if not (destination / ".git").is_dir():
        raise RuntimeError(f"Directory is not a Git repository: {destination}")

    branch = await run("git", "-C", str(destination), "branch", "--show-current")

    if branch != "master":
        raise RuntimeError(f"Unexpected Git branch for {name}: {branch}")

    await run("git", "-C", str(destination), "pull", "--ff-only", "origin", "master")


async def sync_all_services() -> None:
    SERVICE_DIR.mkdir(parents=True, exist_ok=True)

    results = await asyncio.gather(
        *(
            sync_service(name, service.url)
            for name, service in DICT_OF_SERVICES.items()
        ),
        return_exceptions=True,
    )

    errors = [
        f"{name}: {result}"
        for name, result in zip(DICT_OF_SERVICES, results)
        if isinstance(result, Exception)
    ]

    if errors:
        raise RuntimeError("Service synchronization failed:\n" + "\n".join(errors))


# endregion


async def install_requirements(name: str) -> None:
    destination = SERVICE_DIR / name.lstrip("/")
    venv = destination / ".venv"
    python = venv / "bin" / "python"

    if not python.exists():
        await run(sys.executable, "-m", "venv", str(venv))

    await run(
        str(python),
        "-m",
        "pip",
        "install",
        "-U",
        "-r",
        "requirements.txt",
        cwd=destination,
    )


async def deploy_service(name: str, url: str) -> None:
    await sync_service(name, url)
    await install_requirements(name)


async def deploy_all_services() -> None:
    SERVICE_DIR.mkdir(parents=True, exist_ok=True)

    results = await asyncio.gather(
        *(
            deploy_service(name, service.url)
            for name, service in DICT_OF_SERVICES.items()
        ),
        return_exceptions=True,
    )

    errors = [
        f"{name}: {result}"
        for name, result in zip(DICT_OF_SERVICES, results)
        if isinstance(result, Exception)
    ]

    if errors:
        raise RuntimeError("Service deployment failed:\n" + "\n".join(errors))
