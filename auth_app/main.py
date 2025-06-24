import uvicorn
from fastapi import FastAPI

from auth_app.exeptions.custom import (
    ServiceError,
    TokenError,
    TransactionError,
    UserActivityError,
    UserVerificationError,
)
from auth_app.exeptions.handlers import (
    service_error_handler,
    token_verification_handler,
    transaction_error_handler,
    user_activity_exception_handler,
    user_verification_exception_handler,
)
from auth_app.messages.common import msg_creator
from auth_app.routers.tokens import token_router
from auth_app.routers.users import user_router
from auth_app.services.ses.clients import get_ses_client
from auth_app.services.ses.ses_handler import ses_handler

app = FastAPI()
app.include_router(router=user_router)
app.include_router(router=token_router)

app.add_exception_handler(UserActivityError, user_activity_exception_handler)
app.add_exception_handler(UserVerificationError, user_verification_exception_handler)
app.add_exception_handler(TokenError, token_verification_handler)
app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(TransactionError, transaction_error_handler)


@app.on_event("startup")
async def on_startup() -> None:
    async for ses in get_ses_client():
        await ses_handler.verify_sender(ses)


@app.get('/', tags=['root'])
async def root() -> dict:
    return {
        'title': msg_creator.get_root_title(),
        'description': msg_creator.get_root_description(),
        'paths': {
            'swagger': '/docs',
            'redoc': '/redoc',
        },
    }


if __name__ == '__main__':
    uvicorn.run('auth_app.main:app')
