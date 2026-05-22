import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.db.database import async_session
from app.models.audit import AuditLog
import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User
from sqlalchemy.future import select

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We only want to log API actions
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)
            
        # Get response
        response = await call_next(request)
        
        # Only log successful or specifically meaningful actions
        # Avoid logging raw health checks or auth fetching if unwanted
        if request.url.path in ["/api/v1/auth/token", "/api/v1/auth/register"]:
            return response
            
        # Extract user if available
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email = payload.get("sub")
                if email:
                    async with async_session() as session:
                        result = await session.execute(select(User).filter(User.email == email))
                        user = result.scalars().first()
                        if user:
                            user_id = user.id
            except Exception:
                pass

        # Log asynchronously to DB
        async with async_session() as session:
            # Determine module
            module = "System"
            path = request.url.path
            if "chat" in path:
                module = "AI Assistant"
            elif "documents" in path:
                module = "Document AI"

            audit_log = AuditLog(
                user_id=user_id,
                action=f"{request.method} {request.url.path}",
                module=module,
                details=json.dumps({"status_code": response.status_code}),
                ip_address=request.client.host if request.client else "unknown"
            )
            session.add(audit_log)
            await session.commit()
            
        return response
