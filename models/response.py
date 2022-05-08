from aws_lambda_typing import responses

cors_headers = {
  'Content-Type': 'application/json',
  'Allow': '*',
  'Access-Control-Allow-Headers': '*',
  'Access-Control-Allow-Methods': '*',
  'Access-Control-Allow-Origin': '*',
}

class HttpResponse(dict):
  def __init__(self, code: int, body: str):
    r: responses.APIGatewayProxyResponseV2 = {}
    r['statusCode'] = code
    r['body'] = body
    r['headers'] = cors_headers
    dict.__init__(self, **r)

class HttpSuccess(HttpResponse):
  def __init__(self, body: str = ''):
      super().__init__(200, body)

class HttpFailure(HttpResponse):
  def __init__(self, body: str = ''):
      super().__init__(500, body)