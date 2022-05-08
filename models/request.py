from typing import TypedDict

class LoginRequest(TypedDict):
  email: str
  password: str

class RegisterRequest(TypedDict):
  email: str
  password: str
  passwordConfirm: str
  spotifyCode: str