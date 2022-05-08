import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3_type_annotations.dynamodb import Client

from models.documents import Profile

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
  
  def get_spotify_profile(self, id: str):
    r = self.client.get_item(
      TableName='SpotifyProfile',
      Key={ 'spotifyId': { 'S': id } }
    )
    return self.to_object(r.get('Item'))

  def put_spotify_profile(self, profile: Profile):
    return self.client.put_item(
      TableName='SpotifyProfile',
      Item=self.to_document(profile)
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