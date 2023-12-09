import boto3
import json

dynamodbTableName = 'name-of-your-dynamodb-table' # Replace with your DynamoDB table name
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') # Replace with your AWS Region
userTable = dynamodb.Table(dynamodbTableName)

s3 = boto3.client('s3')
bucketName = 'your-bucket' # Replace with your S3 bucket name

def lambda_handler(event, context):

    userId = event['queryStringParameters']['userId']
    try:
        hashKey = event['queryStringParameters']['hashKey']
    except KeyError:
        # Handle the case when 'hashKey' is not present
        hashKey = None  # You can set it to a default value or handle it as needed

    if(hashKey):
      prefix = f'name_folder/{userId}/' # Replace with your prefix
      source_file = check_hash_exist(prefix, hashKey)

      if source_file:
          response_message = 'Hash encontrado!'
          response_status = 200
      else:
          # TODO implement
          response_message = 'Hash desconhecido!'
          response_status = 404
    else:
        user_exist = check_userId_exist(userId)

        if user_exist:
            response_message = 'Usuario cadastrado!'
            response_status = 200
        else:
            response_message = 'Usuario sem cadastrado!'
            response_status = 404

    return buildResponse(response_status, {
        'message': response_message,
        'status': response_status
    })


# Check if user exist (user)
def check_userId_exist(userId):
    # Check if the user already exists based on userId
    scan_result = userTable.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('userId').eq(userId)
    )
    if scan_result['Items']:
      return scan_result['Items'][0]
    else:
      return None

# Get list of objects by prefix (user)
def check_hash_exist(prefix, hashKey):
    response = s3.list_objects_v2(Bucket=bucketName, Prefix=prefix)
    objects = response.get('Contents', [])
    return [object['Key'] for object in objects if hashKey in object['Key']]

# Build response
def buildResponse(statusCode, body=None):
  response = {
    'statusCode': statusCode,
    'headers': {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  }
  if body is not None:
    response['body'] = json.dumps(body)
  return response
