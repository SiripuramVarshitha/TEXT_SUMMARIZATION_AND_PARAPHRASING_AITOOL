from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        
    def verify_jwt(self, jwtoken: str) -> bool:
        # from .auth import verify_token
        #   # <- relative import
        from backend.api.auth import verify_token
        try:
            payload = verify_token(jwtoken)
            return payload is not None
        except:
            return False

# from fastapi import Request, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from typing import Optional

# class JWTBearer(HTTPBearer):
#     def __init__(self, auto_error: bool = True):
#         super(JWTBearer, self).__init__(auto_error=auto_error)

#     async def __call__(self, request: Request) -> str:
#         """
#         Override __call__ to validate the JWT token from Authorization header.
#         """
#         credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTBearer, self).__call__(request)
        
#         if not credentials:
#             raise HTTPException(status_code=403, detail="Authorization header missing.")
        
#         if credentials.scheme.lower() != "bearer":
#             raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        
#         if not self.verify_jwt(credentials.credentials):
#             raise HTTPException(status_code=403, detail="Invalid or expired token.")
        
#         return credentials.credentials

#     def verify_jwt(self, jwtoken: str) -> bool:
#         """
#         Verify JWT token using the auth.verify_token function.
#         """
#         try:
#             from .auth import verify_token  # relative import
#             payload = verify_token(jwtoken)
#             return payload is not None
#         except Exception:
#             return False

