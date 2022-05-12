from typing import TypedDict

class Profile(TypedDict):
  spotifyId: str
  tokenJson: str
  displayName: str
  displayPicture: str
  created: int
  userAgent: str
  ipAddress: str