import os
from xmlrpc.client import Boolean
import jwt
import bcrypt
from datetime import datetime

class AuthClient:
  def __init__(self):
      pass

  @property
  def now(self) -> int:
    return int(datetime.utcnow().timestamp()) * 1000

  def hash_password(self, password: str, salt) -> tuple[str, str]:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return salt, hashed

  def check_password(self, password: str, hash: str) -> bool:
    return bcrypt.checkpw(password, hash)

  def sign_jwt(self, data: dict) -> str:
    return jwt.encode({
      'data': data,
      'expires': self.now + 1000 * 60 * 60 * 8
    }, os.environ.get('JwtSecret'))

  def decode_jwt(self, token: str):
    return jwt.decode(token, os.environ.get('JwtSecret'))