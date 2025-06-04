import uvicorn
from fastapi import FastAPI

from auth_app.routers.users import user_router

app = FastAPI()
app.include_router(router=user_router)


@app.get('/', tags=['temp'])
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
