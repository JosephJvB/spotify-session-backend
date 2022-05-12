import logging
import json
import traceback
from uuid import uuid4
from aws_lambda_typing import context as context_, events, responses
from clients.auth import AuthClient
from clients.ddb import DdbClient
from clients.helpers import now_ts, run_io_tasks_in_parallel
from clients.spotify import SpotifyClient
from models.documents import Session, User, Profile
from models.response import HttpFailure, HttpSuccess
from models.request import LoginRequest
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

    request: LoginRequest = json.loads(event['body'])
    required = ['email', 'password']
    missing = [p for p in required if not request.get(p)]
    if len(missing) > 0:
      m = 'Invalid request, missing properties ' + ', '.join(missing)
      logger.warn(m)
      return HttpFailure(400, m)

    user: User = ddb.get_user(request['email'])
    if user is None:
      m = 'User not found with email ' + request['email']
      logger.warn(m)
      return HttpFailure(400, m)

    pw_match = auth.check_password(request['password'], user['hash'])
    if not pw_match:
      m = 'Password does not match'
      logger.warn(m)
      return HttpFailure(400, m)

    profile: Profile = ddb.get_spotify_profile(user['spotifyId'])
    # todo: make persist session optional
    session: Session = {}
    session['sessionId'] = str(uuid4())
    session['spotifyId'] = profile['spotifyId']
    session['ipAddress'] = event['requestContext']['identity']['sourceIp']
    session['userAgent'] = event['requestContext']['identity']['userAgent']
    session['displayName'] = profile.get('displayName')
    session['displayPicture'] = profile.get('displayPicture')
    session['ts'] = now_ts()

    # todo: check if image or access_token has changed, if yes - save, otherwise skip
    ddb.put_session(session)

    tokens = run_io_tasks_in_parallel([
      lambda: auth.sign_jwt({
        'email': user['email'],
        'spotifyId': user['spotifyId'],
        'expires': now_ts() + 1000 * 60 * 60 * 8,
      }),
      lambda: auth.sign_jwt({
        'sessionId': session['sessionId']
      })
    ])
    jwt, session_token = tokens

    return HttpSuccess(json.dumps({
      'message': 'Login success',
      'token': jwt,
      'sessionToken': session_token,
      'displayPicture': profile.get('displayPicture'),
      'displayName': profile.get('displayName'),
      'spotifyId': user['spotifyId'],
    }))

  except Exception:
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('handler failed')
    return HttpFailure(500, tb)