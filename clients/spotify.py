import logging
import os
import requests
from base64 import b64encode
from clients.helpers import now_ts

from models.spotify import SpotifyRefreshResponse, SpotifyToken

logger = logging.getLogger()
class SpotifyClient:
  basic_auth = ''
  def __init__(self) -> None:
    auth_str = f"{os.environ.get('SpotifyClientId')}:{os.environ.get('SpotifyClientSecret')}"
    self.basic_auth = b64encode(auth_str.encode()).decode()

  def submit_code(self, code: str, redirect_uri: str) -> SpotifyToken:
    logger.info('SpotifyClient.submit_code()')
    logger.info('code ' + code)
    logger.info('basicAuth ' + self.basic_auth)
    r = requests.post('https://accounts.spotify.com/api/token', params={
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri or os.environ.get('SpotifyRedirectUri')
    }, headers={
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': f'Basic {self.basic_auth}',
    })
    if not r.ok:
      logger.error(r.text)
      logger.error(r.status_code)
    r.raise_for_status()
    return r.json()

  def validate_token(self, token: SpotifyToken):
    logger.info('SpotifyClient.validate_token()')
    now = now_ts()
    if now > token['ts'] + token['expires_in'] * 1000:
      refreshed: SpotifyRefreshResponse = self.refresh_token(token)
      token['access_token'] = refreshed['access_token']
      token['ts'] = now
  
  def refresh_token(self, token: SpotifyToken) -> SpotifyRefreshResponse:
    logger.info('SpotifyClient.refresh_token()')
    r = requests.post('https://accounts.spotify.com/api/token', params={
      'grant_type': 'refresh_token',
      'refresh_token': token['refresh_token']
    }, headers={
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': f'Basic {self.basic_auth}',
    })
    r.raise_for_status()
    return r.json()

  def get_profile(self, token: SpotifyToken):
    logger.info('SpotifyClient.get_profile()')
    self.validate_token(token)
    logger.info('access_token ' + token['access_token'])
    r = requests.get('https://api.spotify.com/v1/me', headers ={
      'Authorization': f"Bearer {token['access_token']}"
    })
    if not r.ok:
      logger.error(r.text)
      logger.error(r.status_code)
    r.raise_for_status()
    return r.json()
