# mypy: no-disallow-untyped-decorators
import contextlib
from datetime import datetime

import anyio
import pytest
from asynctor.timing import Timer
from httpx import AsyncClient, ConnectError

from fastapi_cdn_host.cli import load_bool
from fastapi_cdn_host.client import CdnHostBuilder


async def wait_for_app_startup(client: AsyncClient, timeout=5) -> None:
    interval = 0.5
    verbose = load_bool("FASTCDN_VERBOSE")
    timer = Timer("Testing api reachable", decimal_places=3, verbose=verbose)
    start = timer._start

    def past_time() -> float:
        return round(datetime.now().timestamp() - start, timer._decimal_places)

    for loop in range(1, int(timeout // interval)):
        with contextlib.suppress(ConnectError), timer as t:
            r = await client.get("/app", timeout=1)
            if r.status_code == 200:
                if verbose:
                    print(f"API ready within loop {loop}, Cost: {past_time()} seconds")
                return
        if (delta := interval - t.cost) > 0:
            await anyio.sleep(delta)
        if past_time() > timeout:
            break


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    await wait_for_app_startup(client)
    swagger_ui = CdnHostBuilder.swagger_files
    js_url = "/static/" + swagger_ui["js"]
    css_url = "/static/" + swagger_ui["css"]
    response = await client.get(css_url)
    assert response.status_code == 200, f"{response.url=};{response.text=}"
    response = await client.get(js_url)
    assert response.status_code == 200, response.text
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert js_url in text
    assert css_url in text
    response = await client.get("/redoc")
    text = response.text
    assert response.status_code == 200, text
    assert "/static/redoc" in text
    response = await client.get("/app")
    assert response.status_code == 200
