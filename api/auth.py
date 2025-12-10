from ninja.security import HttpBearer

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        if hasattr(request.user, 'organization'):
            return request.user
        
        if hasattr(request, 'jwt_error'):
            return None
        
        return None
        