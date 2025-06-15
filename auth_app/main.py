import uvicorn
from fastapi import FastAPI

from auth_app.exeptions.custom import (
    UserActivityError,
    UserVerificationError,
)
from auth_app.exeptions.handlers import (
    user_activity_exception_handler,
    user_verification_exception_handler,
)
from auth_app.routers.tokens import token_router
from auth_app.routers.users import user_router
from auth_app.services.aws.ses.clients import get_ses_client
from auth_app.services.aws.ses.email_verification import verify_sender

app = FastAPI()
app.include_router(router=user_router)
app.include_router(router=token_router)

app.add_exception_handler(UserActivityError, user_activity_exception_handler)
app.add_exception_handler(UserVerificationError, user_verification_exception_handler)


@app.on_event("startup")
async def on_startup() -> None:
    async for ses in get_ses_client():
        await verify_sender(ses)


@app.get('/', tags=['root'])
async def root() -> dict:
    return {
        'title': 'Skill Tracker Auth',
        'description': 'Auth REST API for the Skill Tracker app',
        'paths': {
            'swagger': '/docs',
            'redoc': '/redoc',
        },
    }


if __name__ == '__main__':
    uvicorn.run('auth_app.main:app')
