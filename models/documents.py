from typing import TypedDict

class Profile(TypedDict):
  spotifyId: str
  tokenJson: str
  displayName: str
  displayPicture: str
  userAgent: str
  ipAddress: str
  lastLogin: int