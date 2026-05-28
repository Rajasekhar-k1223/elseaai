import asyncio
import os

from sqlalchemy.future import select

import app.models  # Ensure all models are loaded in SQLAlchemy registry
from app.db.database import async_session
from app.models.user import Role, User
from app.models.document import DocumentMetadata  # Added to resolve SQLAlchemy relationship
from app.core.security import get_password_hash


ADMIN_EMAIL = os.environ.get("E2E_ADMIN_EMAIL", "admin@elsea.ai")
ADMIN_PASSWORD = os.environ.get("E2E_ADMIN_PASSWORD", "AdminPass123!")


async def seed():
    async with async_session() as session:
        # Ensure role exists
        result = await session.execute(select(Role).filter(Role.name == "Super Admin"))
        role = result.scalars().first()
        if not role:
            role = Role(name="Super Admin", description="Full administrative access")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            print("Created role: Super Admin")
        else:
            print("Role exists: Super Admin")

        # Ensure admin user exists
        result = await session.execute(select(User).filter(User.email == ADMIN_EMAIL))
        user = result.scalars().first()
        if not user:
            hashed = get_password_hash(ADMIN_PASSWORD)
            user = User(email=ADMIN_EMAIL, hashed_password=hashed, full_name="Admin User", role_id=role.id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"Created admin user: {ADMIN_EMAIL}")
        else:
            print(f"Admin user exists: {ADMIN_EMAIL}")


if __name__ == "__main__":
    asyncio.run(seed())
