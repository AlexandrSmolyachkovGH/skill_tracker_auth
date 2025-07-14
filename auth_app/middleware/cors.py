from pydantic import BaseModel


class CORSSettings(BaseModel):
    allow_origins: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


cors_settings = CORSSettings()
