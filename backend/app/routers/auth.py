from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.settings import settings
from app.db.crud.user import create_user, get_user_by_email, update_refresh_token
from app.db.database import get_db
from app.db.schemas.auth import LoginResponse, TokenResponse, UserResponse, UserProfileResponse, UserUpdateRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])

security = HTTPBearer()

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_URL = "https://kapi.kakao.com/v2/user/me"


def _get_kakao_config() -> dict[str, str]:
    client_id = getattr(settings, "kakao_client_id", None)
    redirect_uri = getattr(settings, "kakao_redirect_uri", None)
    client_secret = getattr(settings, "kakao_client_secret", "")

    if not client_id or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kakao OAuth 환경 변수가 설정되지 않았습니다.",
        )

    return {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "client_secret": client_secret,
    }


@router.get("/kakao/login")
async def kakao_login_url() -> dict[str, str]:
    config = _get_kakao_config()
    scope = "profile_nickname"
    authorize_url = (
        f"{KAKAO_AUTH_URL}?response_type=code"
        f"&client_id={config['client_id']}"
        f"&redirect_uri={config['redirect_uri']}"
        f"&scope={scope}"
    )
    return {"authorize_url": authorize_url}


@router.get("/kakao/callback", response_model=LoginResponse)
async def kakao_callback(
    code: str = Query(..., description="Kakao OAuth code"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    config = _get_kakao_config()

    async with httpx.AsyncClient(timeout=10) as client:
        token_res = await client.post(
            KAKAO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": config["client_id"],
                "redirect_uri": config["redirect_uri"],
                "code": code,
                "client_secret": config["client_secret"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if token_res.status_code != 200:
        raise HTTPException(
            status_code=token_res.status_code,
            detail={
                "message": "Kakao 토큰 발급 실패",
                "status": token_res.status_code,
                "body": token_res.text,
            },
        )

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kakao access_token 누락")

    async with httpx.AsyncClient(timeout=10) as client:
        user_res = await client.get(
            KAKAO_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if user_res.status_code != 200:
        raise HTTPException(status_code=user_res.status_code, detail="Kakao 사용자 조회 실패")

    kakao_user = user_res.json()
    kakao_account = kakao_user.get("kakao_account") or {}
    profile = kakao_account.get("profile") or {}

    email = kakao_account.get("email")
    if not email:
        kakao_id = kakao_user.get("id")
        if not kakao_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카카오 사용자 식별자를 확인할 수 없습니다.",
            )
        email = f"kakao_{kakao_id}@kakao.local"

    username = profile.get("nickname") or email.split("@")[0]

    user = await get_user_by_email(db, email)
    if not user:
        user = await create_user(db, email=email, username=username, social_type="kakao")

    app_access = create_access_token(str(user.user_id))
    app_refresh = create_refresh_token(str(user.user_id))
    await update_refresh_token(db, user.user_id, app_refresh)

    return LoginResponse(
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            social_type=user.social_type,
        ),
        tokens=TokenResponse(access_token=app_access, refresh_token=app_refresh),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh 토큰이 아닙니다.")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰 정보가 올바르지 않습니다.")

    # SQLAlchemy AsyncSession.get needs model class
    from app.db.models.user import User

    user = await db.get(User, int(user_id))
    if not user or user.refresh_token != credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh 토큰이 일치하지 않습니다.")

    new_access = create_access_token(str(user.user_id))
    return TokenResponse(access_token=new_access, refresh_token=credentials.credentials)


async def _get_current_user(
    credentials: HTTPAuthorizationCredentials,
    db: AsyncSession,
):
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access 토큰이 아닙니다.")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰 정보가 올바르지 않습니다.")
    from app.db.models.user import User
    user = await db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
    return user


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user = await _get_current_user(credentials, db)
    return UserProfileResponse(
        user_id=user.user_id,
        email=user.email,
        username=user.username,
        social_type=user.social_type,
        age=user.age,
        guardian_contact=user.guardian_contact,
    )


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    payload: UserUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user = await _get_current_user(credentials, db)
    if payload.username is not None:
        user.username = payload.username
    if payload.age is not None:
        user.age = payload.age
    if payload.guardian_contact is not None:
        user.guardian_contact = payload.guardian_contact
    await db.commit()
    await db.refresh(user)
    return UserProfileResponse(
        user_id=user.user_id,
        email=user.email,
        username=user.username,
        social_type=user.social_type,
        age=user.age,
        guardian_contact=user.guardian_contact,
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh 토큰이 아닙니다.")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰 정보가 올바르지 않습니다.")

    await update_refresh_token(db, int(user_id), None)
    return {"message": "로그아웃되었습니다."}
