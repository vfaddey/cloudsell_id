from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from starlette import status
from fastapi import APIRouter, Depends, HTTPException

from src.api import deps
from src.api.deps import get_user_service, get_current_user
from src.exceptions.base import CloudsellIDException
from src.exceptions.user import UserNotFound, AlreadyConfirmed, AuthorizationException
from src.schemas.token import FullToken, RefreshTokenRequest
from src.schemas.user import UserCreate, UserOut
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

@router.get('/forgot-password')
async def reset_password(email: EmailStr,
                         user_service: UserService = Depends(get_user_service)):
    try:
        await user_service.send_password_reset_email(email)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CloudsellIDException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch('/reset-password', include_in_schema=False)
async def reset_password(token: str):
    ...


@router.get('/confirm-email')
async def confirm_email(token: str,
                        user_service: UserService = Depends(get_user_service)):
    try:
        result = await user_service.confirm_email(token)
        return result
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CloudsellIDException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get('/confirm-email/send')
async def send_confirmation_email(user: UserOut = Depends(get_current_user),
                                  user_service: UserService = Depends(get_user_service)):
    try:
        result = await user_service.send_confirmation_email(user)
        return result
    except AlreadyConfirmed as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(e))
    except CloudsellIDException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))