from datetime import datetime
import os
import requests
from base64 import b64encode
from clients.helpers import now_ts

from models.spotify import SpotifyRefreshResponse, SpotifyToken

class SpotifyClient:
  basic_auth = ''
  def __init__(self) -> None:
    auth_str = f"{os.environ.get('SpotifyClientId')}:{os.environ.get('SpotifyClientSecret')}"
    self.basic_auth = b64encode(auth_str.encode()).decode()

  def validate_token(self, token: SpotifyToken):
    now = now_ts()
    if now > token['ts'] + token['expires_in'] * 1000:
      refreshed = self.refresh_token(token)
      token['access_token'] = refreshed['access_token']
      token['ts'] = now
  
  def refresh_token(self, token: SpotifyToken) -> SpotifyRefreshResponse:
    r = requests.post('https://accounts.spotify.com/api/token', params={
      'grant_type': 'refresh_token',
      'refresh_token': token['refresh_token']
    }, headers={
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': f'Basic {self.basic_auth}',
    })
    return r.json()

  def get_profile(self, token: SpotifyToken):
    self.validate_token(token)
    r = requests.get('https://api.spotify.com/v1/me', headers ={
      'Authorization': f"Bearer {token['access_token']}"
    })
    return r.json()