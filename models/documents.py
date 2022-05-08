from typing import TypedDict

class User(TypedDict):
  email: str
  hash: str
  salt: str
  created: int
  spotifyId: str

class Profile(TypedDict):
  spotifyId: str
  tokenJson: str
  displayName: str
  displayPicture: str