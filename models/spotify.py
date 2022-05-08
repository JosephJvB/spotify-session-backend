from typing import Type, TypedDict

class SpotifyTokenResponse(TypedDict):
  access_token: str
  token_type: str
  expires_in: int
  refresh_token: str
  scope: str

class SpotifyToken(SpotifyTokenResponse):
  ts: int

class SpotifyRefreshResponse(TypedDict):
  access_token: str
  token_type: str
  scope: str
  expires_in: int

class SpotifyImage(TypedDict):
  height: int
  url: str
  width: int

class SpotifyProfileResponse(TypedDict):
  country: str
  display_name: str
  email: str
  href: str
  id: str
  images: list[SpotifyImage]
  product: str
  type: str
  uri: str