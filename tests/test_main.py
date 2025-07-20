import pytest

from main import root

@pytest.mark.asyncio
async def test_root():
    resp = await root()

    assert resp == {"message": "Hello, World!"}