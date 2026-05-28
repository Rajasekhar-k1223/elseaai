import asyncio
from sqlalchemy.future import select
from app.db.database import async_session
from app.models.user import User
from app.core.security import get_password_hash

async def update():
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.email=='admin@elsea.ai'))
        user = result.scalars().first()
        if user:
            user.hashed_password = get_password_hash('AdminPass123!')
            await session.commit()
            print('Password updated successfully!')
        else:
            print('User not found.')

if __name__ == "__main__":
    asyncio.run(update())
