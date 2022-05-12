import os
from xmlrpc.client import Boolean
import jwt
from clients.helpers import now_ts

from models.request import JWT, JWTData
class AuthClient:
  def __init__(self):
      pass

  def sign_jwt(self, data: JWTData) -> str:
    return jwt.encode({
      'data': data
    }, os.environ.get('JwtSecret'))

  def decode_jwt(self, token: str) -> JWT:
    return jwt.decode(token, os.environ.get('JwtSecret'), algorithms=['HS256'])