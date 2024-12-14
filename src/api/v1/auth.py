from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from fastapi import APIRouter, Depends, HTTPException

from src.api import deps
from src.api.deps import get_user_service
from src.exceptions.base import CloudsellIDException
from src.schemas.token import FullToken, RefreshTokenRequest
from src.schemas.user import UserCreate
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post('/register', response_model=FullToken)
async def register_user(user_data: UserCreate,
                        user_service: UserService = Depends(deps.get_user_service)):
    try:
        token = await user_service.create(user_data)
        return token
    except CloudsellIDException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                user_service: UserService = Depends(get_user_service)):
    email = form_data.username
    password = form_data.password
    try:
        token = await user_service.authenticate_user(email, password)
        return token
    except CloudsellIDException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post('/refresh')
async def refresh_access_token(request: RefreshTokenRequest,
                               user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.refresh_token(request.refresh_token)
    except CloudsellIDException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get('/forgot-password', include_in_schema=False)
async def reset_password():
    ...

@router.post('/reset-password', include_in_schema=False)
async def reset_password():
    ...

@router.get('/confirm-email', include_in_schema=False)
async def confirm_email(token: str):
    ...