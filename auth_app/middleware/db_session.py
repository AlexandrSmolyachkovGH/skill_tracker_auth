from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from auth_app.db.connect_db import AsyncSessionLocal


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        async with AsyncSessionLocal() as session:
            request.state.db = session
            try:
                await session.begin()
                response = await call_next(request)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return response


def get_db_from_request(request: Request) -> AsyncSession:
    return request.state.db
