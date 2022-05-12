import logging
import json
import traceback
from aws_lambda_typing import context as context_, events, responses
from clients.auth import AuthClient
from clients.ddb import DdbClient
from clients.helpers import now_ts
from models.documents import Profile
from models.http import JWT, HttpFailure, HttpSuccess

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ddb = DdbClient()
auth = AuthClient()

def handler(event: events.APIGatewayProxyEventV1, context: context_.Context)-> responses.APIGatewayProxyResponseV1:
  try:
    logger.info('method ' + event['httpMethod'])
    if event['httpMethod'] == 'OPTIONS':
      return HttpSuccess()

    jwt = (event['headers'].get('Authorization') or '').replace('Bearer ', '')
    if not jwt:
      m = 'Invalid request, missing token'
      logger.warn(m)
      return HttpFailure(400, m)

    decoded: JWT = auth.decode_jwt(jwt)
    if not decoded or not decoded.get('data'):
      m = 'Invalid request, jwt invalid'
      logger.warn(m)
      return HttpFailure(400, m)
    if not decoded.get('sessionId'):
      m = 'Invalid request, jwt invalid. Missing sessionId'
      logger.warn(m)
      return HttpFailure(400, m)
    if now_ts() > decoded.get('expires'):
      m = 'Invalid request, jwt expired'
      logger.warn(m)
      return HttpFailure(400, m)

    profile: Profile = ddb.get_spotify_profile(decoded['spotifyId'])
    if not profile:
      m = 'Invalid request, profile not found with id ' + decoded['sessionId']
      logger.warn(m)
      return HttpFailure(400, m)

    ip = event['requestContext']['identity']['sourceIp']
    ua = event['requestContext']['identity']['userAgent']
    if profile['ipAddress'] != ip or profile['userAgent'] != ua:
      m = 'Invalid request, ip or user agent do not match profile'
      logger.warn(m)
      return HttpFailure(400, m)

    jwt = auth.sign_jwt({
      'spotifyId': profile['spotifyId'],
      'expires': now_ts() + 1000 * 60 * 60 * 8,
    })

    return HttpSuccess(json.dumps({
      'message': 'ValidateJwt success',
      'token': jwt,
      'spotifyId': profile['spotifyId'],
      'displayPicture': profile['displayPicture'],
      'displayName': profile['displayName'],
    }))

  except Exception:
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('handler failed')
    return HttpFailure(500, tb)