import os
from xmlrpc.client import Boolean
import jwt
import bcrypt

from models.request import JWT, JWTData
class AuthClient:
  def __init__(self):
      pass

  def hash_password(self, password: str) -> tuple[str, str]:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)
    return salt, hashed

  def check_password(self, password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf8'), hash.encode('utf8'))

  def sign_jwt(self, data: JWTData) -> str:
    return jwt.encode({
      'data': data
    }, os.environ.get('JwtSecret'))

  def decode_jwt(self, token: str) -> JWT:
    return jwt.decode(token, os.environ.get('JwtSecret'), algorithms=['HS256'])