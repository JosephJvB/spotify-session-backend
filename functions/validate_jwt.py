import logging
import json
import traceback
from aws_lambda_typing import context as context_, events, responses
from clients.auth import AuthClient
from clients.ddb import DdbClient
from clients.helpers import now_ts
from models.response import HttpFailure, HttpSuccess

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ddb = DdbClient()
auth = AuthClient()

def handler(event: events.APIGatewayProxyEventV1, context: context_.Context)-> responses.APIGatewayProxyResponseV1:
  try:
    logger.info('method ' + event['httpMethod'])
    logger.info('body ' + (event['body'] or '{}'))
    if event['httpMethod'] == 'OPTIONS':
      return HttpSuccess()

    jwt = (event['headers'].get('Authorization') or '').replace('Bearer ', '')
    if not jwt:
      m = 'Invalid request, missing token'
      logger.warn(m)
      return HttpFailure(400, m)
    
    decoded = auth.decode_jwt(jwt)
    if not decoded or not decoded.get('data'):
      m = 'Invalid request, jwt invalid'
      logger.warn(m)
      return HttpFailure(400, m)
    required = ['spotifyId', 'email', 'expires']
    missing = [k for k in required if not decoded['data'].get(k)]
    if len(missing) > 0:
      m = 'Invalid request, jwt invalid. Missing properties ' + ', '.join(missing)
      logger.warn(m)
      return HttpFailure(400, m)
    if decoded['data']['expires'] < now_ts():
      m = 'Invalid request, jwt expired'
      logger.warn(m)
      return HttpFailure(400, m)

    profile = ddb.get_spotify_profile(decoded['data']['spotifyId'])
    if not profile:
      m = 'Invalid request, no spotify profile save with id ' + decoded['data']['spotifyId']
      logger.warn(m)
      return HttpFailure(400, m)
    
    jwt = auth.sign_jwt({
      'email': decoded['data']['email'],
      'spotifyId': decoded['data']['spotifyId'],
    })

    return HttpSuccess(json.dumps({
      'message': 'ValidateJwt success',
      'token': jwt,
      'email': decoded['data']['email'],
      'spotifyId': decoded['data']['spotifyId'],
      'displayPicture': profile['displayPicture'],
      'displayName': profile['displayName'],
    }))

  except Exception:
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('handler failed')
    return HttpFailure(500, tb)