import os
import jwt
from models.http import JWT

class AuthClient:
  def __init__(self):
      pass

  def sign_jwt(self, data: JWT) -> str:
    return jwt.encode({
      'data': data
    }, os.environ.get('JwtSecret'))

  def decode_jwt(self, token: str) -> JWT:
    return jwt.decode(token, os.environ.get('JwtSecret'), algorithms=['HS256'])