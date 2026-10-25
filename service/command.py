import asyncio
from pathlib import Path


async def run(*args: str, cwd: Path | None = None) -> str:
    process = await asyncio.create_subprocess_exec(
        *args,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    output, _ = await process.communicate()
    result = output.decode(errors="replace").strip()

    if process.returncode != 0:
        raise RuntimeError(
            f"Command {' '.join(args)} failed ({process.returncode}): {result}"
        )

    return result
