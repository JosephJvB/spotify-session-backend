import logging
import json
import traceback
from aws_lambda_typing import context as context_, events, responses
from clients.auth import AuthClient
from clients.ddb import DdbClient
from clients.helpers import now_ts, run_io_tasks_in_parallel
from clients.spotify import SpotifyClient
from models.documents import User, Profile
from models.response import HttpFailure, HttpSuccess
from models.request import RegisterRequest
from models.spotify import SpotifyProfileResponse, SpotifyToken

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ddb = DdbClient()
spotify = SpotifyClient()
auth = AuthClient()

def handler(event: events.APIGatewayProxyEventV1, context: context_.Context)-> responses.APIGatewayProxyResponseV1:
  try:
    logger.info('method ' + event['httpMethod'])
    logger.info('body ' + (event['body'] or '{}'))
    if event['httpMethod'] == 'OPTIONS':
      return HttpSuccess()

    request: RegisterRequest = json.loads(event['body'])
    required = ['email', 'password', 'passwordConfirm', 'spotifyCode']
    missing = [p for p in required if not request.get(p)]
    if len(missing) > 0:
      m = 'Invalid request, missing properties ' + ', '.join(missing)
      logger.warn(m)
      return HttpFailure(400, m)

    if request['password'] != request['passwordConfirm']:
      m = 'Invalid request, passwords do not match'
      logger.warn(m)
      return HttpFailure(400, m)

    user: User = ddb.get_user(request['email'])
    if user is not None:
      m = 'User exists with email ' + request['email']
      logger.warn(m)
      return HttpFailure(400, m)

    token: SpotifyToken = spotify.submit_code(request['spotifyCode'])
    token['ts'] = now_ts()
    profile_response: SpotifyProfileResponse = spotify.get_profile(token)
    profile: Profile = ddb.get_spotify_profile(profile_response['id'])
    if profile is not None:
      m = 'Spotify profile already registered ' + profile_response['id']
      logger.warn(m)
      return HttpFailure(400, m)
    
    salt, hashed = auth.hash_password(request['password'])
    user: User = {}
    user['created'] = now_ts()
    user['email'] = request['email']
    user['hash'] = hashed
    user['salt'] = salt
    user['spotifyId'] = profile_response['id']

    profile: Profile = {}
    profile['spotifyId'] = profile_response['id']
    profile['tokenJson'] = json.dumps(token)
    profile['displayName'] = profile_response['display_name']
    img_urls = [i['url'] for i in profile_response['images'] if i.get('url')]
    if len(img_urls) > 0:
      profile['displayPicture'] = img_urls[0]

    run_io_tasks_in_parallel([
      lambda: ddb.put_user(user),
      lambda: ddb.put_spotify_profile(profile),
    ])
    jwt = auth.sign_jwt({
      'email': user['email'],
      'spotifyId': user['spotifyId'],
    })

    return HttpSuccess(json.dumps({
      'message': 'Login success',
      'token': jwt,
      'email': user['email'],
      'displayPicture': profile.get('displayPicture'),
      'displayName': profile.get('displayName'),
      'spotifyId': user['spotifyId'],
    }))

  except Exception:
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('handler failed')
    return HttpFailure(500, tb)