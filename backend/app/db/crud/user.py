from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, username: str, social_type: str) -> User:
    user = User(email=email, username=username, social_type=social_type)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_refresh_token(db: AsyncSession, user_id: int, refresh_token: str | None) -> None:
    await db.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(refresh_token=refresh_token)
    )
    await db.commit()
