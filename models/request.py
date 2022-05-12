from typing import TypedDict

class LoginRequest(TypedDict):
  email: str
  password: str

class RegisterRequest(TypedDict):
  email: str
  password: str
  passwordConfirm: str
  spotifyCode: str

class JWTData(TypedDict):
  email: str
  spotifyId: str
  expires: int
class JWT(TypedDict):
  data: JWTData

class SessionJWTData(TypedDict):
  sessionId: str
class SessionJWT(TypedDict):
  data: SessionJWTData