import logging
import json
import os
import traceback
from aws_lambda_typing import context as context_, events, responses
from clients.auth import AuthClient
from clients.ddb import DdbClient
from clients.helpers import now_ts
from clients.spotify import SpotifyClient
from models.documents import Profile
from models.http import HttpFailure, HttpSuccess
from models.spotify import SpotifyProfileResponse, SpotifyTokenResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ddb = DdbClient()
spotify = SpotifyClient()
auth = AuthClient()

def handler(event: events.APIGatewayProxyEventV1, context: context_.Context)-> responses.APIGatewayProxyResponseV1:
  try:
    logger.info('method ' + event['httpMethod'])
    if event['httpMethod'] == 'OPTIONS':
      return HttpSuccess()

    code = event['queryStringParameters'].get('spotifyCode')
    if code is None:
      m = 'Invalid request, missing spotifyCode'
      logger.warn(m)
      return HttpFailure(400, m)


    redirect_uri = event['queryStringParameters'].get('redirect_url_override')
    spotify_token: SpotifyTokenResponse = spotify.submit_code(code, redirect_uri)
    spotify_token['ts'] = now_ts()
    spotify_profile: SpotifyProfileResponse = spotify.get_profile(spotify_token)

    profile: Profile = {}
    profile['spotifyId'] = spotify_profile['id']
    profile['tokenJson'] = json.dumps(spotify_token)
    profile['ipAddress'] = event['requestContext']['identity']['sourceIp']
    profile['userAgent'] = event['requestContext']['identity']['userAgent']
    profile['displayName'] = spotify_profile['display_name']
    profile['lastLogin'] = str(now_ts())
    profile['displayPicture'] = next((i.get('url') for i in spotify_profile['images'] if i.get('url')), None)
    ddb.put_spotify_profile(profile)

    jwt = auth.sign_jwt({
      'spotifyId': profile['spotifyId'],
      'expires': now_ts() + 1000 * 60 * 60 * 8,
    })

    return HttpSuccess(json.dumps({
      'message': 'Login success',
      'token': jwt,
      'displayPicture': profile.get('displayPicture'),
      'displayName': profile.get('displayName'),
      'spotifyId': profile['spotifyId'],
    }))

  except Exception:
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('handler failed')
    return HttpFailure(500, tb)