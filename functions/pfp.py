from typing import TypedDict
import boto3
from boto3_type_annotations.s3 import Client
import logging
import requests
import traceback
from aws_lambda_typing import context as context_, events
from clients.ddb import DdbClient
from models.documents import Session

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ddb = DdbClient()
s3: Client = boto3.client('s3')

def handler(event: events.DynamoDBStreamEvent, context: context_.Context) -> None:
  try:
    logger.info(str(len(event['Records'])) + ' records')
    to_download: list[Session] = []
    for record in event['Records']:
      logger.info(record)
      if record['eventName'] == 'INSERT':
        session: Session = ddb.to_object(record['dynamodb']['NewImage'])
        if session.get('displayPicture'):
          to_download.append(session)

    logger.info(str(len(to_download)) + ' images to download')
    if len(to_download) == 0:
      return

    i = 1
    for session in to_download:
      logger.info(f'download {i} / {len(to_download)}')
      i += 1
      r = requests.get(session['displayPicture'], stream=True)
      key = 'pfp/' + session['spotifyId'] + '.jpg'
      s3.put_object(
        Bucket='jvb-media',
        Key=key,
        Body=r.content,
        ACL='public-read',
        ContentType='image/jpeg'
      )
      url = f'https://jvb-media.s3.ap-southeast-2.amazonaws.com/{key}'
      ddb.update_session_pfp(session['sessionId'], url)
      ddb.update_spotify_profile_pfp(session['spotifyId'], url)

  except Exception:
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('handler failed')