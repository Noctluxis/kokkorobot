import httpx
from httpx import Response
from retrying import retry


@retry(stop_max_attempt_number=5, wait_fixed=3100)
async def get(url: str, *args, **kwargs) -> Response:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, *args, **kwargs)
        return resp


@retry(stop_max_attempt_number=5, wait_fixed=3100)
async def post(url: str, *args, **kwargs) -> Response:
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, *args, **kwargs)
        return resp


@retry(stop_max_attempt_number=5, wait_fixed=3100)
async def head(url: str, *args, **kwargs) -> Response:
    async with httpx.AsyncClient() as client:
        resp = await client.head(url, *args, **kwargs)
        return resp
