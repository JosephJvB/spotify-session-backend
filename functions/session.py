from cProfile import Profile
from ipaddress import ip_address
import logging
import json
import traceback
from aws_lambda_typing import context as context_, events, responses
from clients.auth import AuthClient
from clients.ddb import DdbClient
from clients.helpers import now_ts, run_io_tasks_in_parallel
from models.documents import Session, User
from models.request import JWT
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
    
    decoded: JWT = auth.decode_jwt(jwt)
    if not decoded or not decoded.get('data'):
      m = 'Invalid request, jwt invalid'
      logger.warn(m)
      return HttpFailure(400, m)
    if not decoded['data'].get('sessionId'):
      m = 'Invalid request, jwt invalid. Missing sessionId'
      logger.warn(m)
      return HttpFailure(400, m)

    session: Session = ddb.get_session(decoded['data']['sessionId'])
    if not session:
      m = 'Invalid request, session not found with id ' + decoded['data']['sessionId']
      logger.warn(m)
      return HttpFailure(400, m)

    ip = event['requestContext']['identity']['sourceIp']
    ua = event['requestContext']['identity']['userAgent']
    if session['ipAddress'] != ip or session['userAgent'] != ua:
      m = 'Invalid request, ip or user agent do not match session'
      logger.warn(m)
      return HttpFailure(400, m)

    jwt = auth.sign_jwt({
      'email': session['email'],
      'spotifyId': session['spotifyId'],
    })

    return HttpSuccess(json.dumps({
      'message': 'ValidateJwt success',
      'token': jwt,
      'spotifyId': session['spotifyId'],
      'displayPicture': session['displayPicture'],
      'displayName': session['displayName'],
    }))

  except Exception:
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('handler failed')
    return HttpFailure(500, tb)