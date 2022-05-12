import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3_type_annotations.dynamodb import Client

from models.documents import Profile, Session, User
class DdbClient():
  client: Client
  td: TypeDeserializer
  ts: TypeSerializer
  def __init__(self):
    self.client = boto3.client('dynamodb')
    self.td = TypeDeserializer()
    self.ts = TypeSerializer()

  def get_user(self, email: str):
    r = self.client.get_item(
      TableName='JafMembers',
      Key={ 'email': { 'S': email } }
    )
    return self.to_object(r.get('Item'))

  def put_user(self, user: User):
    self.client.put_item(
      TableName='JafMembers',
      Item=self.to_document(user)
    )
  
  def get_spotify_profile(self, id: str):
    r = self.client.get_item(
      TableName='SpotifyProfile',
      Key={ 'spotifyId': { 'S': id } }
    )
    return self.to_object(r.get('Item'))

  def put_spotify_profile(self, profile: Profile):
    self.client.put_item(
      TableName='SpotifyProfile',
      Item=self.to_document(profile)
    )

  def update_spotify_profile_pfp(self, id: str, url: str):
    self.client.update_item(
      TableName='SpotifyProfile',
      Key={ 'spotifyId': { 'S': id } },
      AttributeUpdates={
        'displayPicture': { 'S': url }
      },
      Action='PUT'
    )

  def get_session(self, id: str):
    r = self.client.get_item(
      TableName='JafSessions',
      Key={ 'sessionId': { 'S': id } }
    )
    return self.to_object(r.get('Item'))

  def delete_session(self, id: str):
    self.client.delete_item(
      TableName='JafSessions',
      Key={ 'sessionId': { 'S': id } }
    )

  def put_session(self, session: Session):
    self.client.put_item(
      TableName='JafSessions',
      Item=self.to_document(session)
    )

  def update_session_pfp(self, id: str, url: str):
    self.client.update_item(
      TableName='JafSessions',
      Key={ 'sessionId': { 'S': id } },
      AttributeUpdates={
        'displayPicture': { 'S': url }
      },
      Action='PUT'
    )

  def to_document(self, obj: dict):
    return {
      k: self.ts.serialize(v) for k, v in obj.items()
    }
  def to_object(self, item: dict):
    if not item:
      return None
    return {
      k: self.td.deserialize(item[k]) for k in item.keys()
    }