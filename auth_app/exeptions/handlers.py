from fastapi import Request, status
from fastapi.responses import JSONResponse

from auth_app.exeptions.custom import (
    UserActivityError,
    UserVerificationError,
)


async def user_verification_exception_handler(
        request: Request,
        exc: UserVerificationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


async def user_activity_exception_handler(
        request: Request,
        exc: UserActivityError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )
