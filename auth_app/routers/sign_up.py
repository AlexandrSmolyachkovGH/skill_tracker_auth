from fastapi import APIRouter, Depends, HTTPException, Path, status

from auth_app.schemas.sign_up import (
    CreateUser,
    GetUser,
    PatchUser,
)

router = APIRouter(
    prefix='/sign-in',
    tags=['sign-in'],
)
