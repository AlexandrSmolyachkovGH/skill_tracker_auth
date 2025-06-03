import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get('/', tags=['temp'])
async def temp() -> dict:
    return {
        'key': 'value',
    }


if __name__ == '__main__':
    uvicorn.run('auth_app.main:app', host="0.0.0.0", port=8081, reload=True)
