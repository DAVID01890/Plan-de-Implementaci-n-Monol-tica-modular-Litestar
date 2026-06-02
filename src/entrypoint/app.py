from litestar import Litestar, get


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> Litestar:
    return Litestar(route_handlers=[health])
