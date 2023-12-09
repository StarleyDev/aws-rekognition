# Description: Detect faces in an image and compare them with a target image
# Event: user_registration.py
# Author: Starley Cazorla
# Version: 1.0
# Language: python
# Runtime: python3.7
# License: MIT

import boto3
import datetime

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1') # Replace with your AWS Region
dynamodbTableName = 'name-of-your-dynamodb-table' # Replace with your DynamoDB table name
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') # Replace with your AWS Region
userTable = dynamodb.Table(dynamodbTableName)
bucketName = 'your-bucket' # Replace with your S3 bucket name

def lambda_handler(event, context):
  print(event)
  key = event['Records'][0]['s3']['object']['key']

  extract = key.split('/')
  userId = extract[1]
  userName = ' '.join(extract[2].split('_')[0:-1])
  try:
    response = index_faces(bucketName, key)
    print('Entrou no response do bucket', bucketName, key)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
      faceId = response['FaceRecords'][0]['Face']['FaceId']

      registerOrUpdateUser(faceId, userName, userId)
    return response
  except Exception as e:
    print(e)
    raise e

def index_faces(bucketName, key):
  response = rekognition.index_faces(
    Image={
      'S3Object': {
        'Bucket': bucketName,
        'Name': key
      }
    },
    CollectionId='user-facemacth',
  )
  return response

def registerOrUpdateUser(faceId, userName, userId):
    try:

         # Obtenha a data e hora atual
        current_datetime = datetime.datetime.now()
        # Subtrai 3 horas para ajustar para o fuso horário de São Paulo (UTC-03:00)
        sao_paulo_datetime = current_datetime - datetime.timedelta(hours=3)
        # Converta a data e hora ajustada para formato ISO
        current_date = sao_paulo_datetime.isoformat()

        scan_result = userTable.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('userId').eq(userId)
        )

        registration_count, audit_count = get_image_count(userId)

        if scan_result['Items']:
            # User with the same userId exists, update the firstName and lastName
            user = scan_result['Items'][0]
            response = userTable.update_item(
                Key={'rekognitionId': user['rekognitionId']},
                UpdateExpression='SET registration_count = :fn, audit_count = :ln, lastRekognition = :lr',
                ExpressionAttributeValues={
                    ':fn': registration_count,
                    ':ln': audit_count,
                    ':lr': current_date
                },
                ReturnValues="UPDATED_NEW"
            )
        else:
            # User with the same userId doesn't exist, create a new user
            userTable.put_item(
                Item={
                    'rekognitionId': faceId,
                    'userId': userId,
                    'userName': userName,
                    'registrationDate': current_date
                }
            )
            response = "User created successfully"

        return response
    except Exception as e:
        return str(e)


def get_image_count(userId):

    # Contagem de imagens cadastradas
    registration_prefix = f'name_folder/{userId}/' # Replace with your prefix
    registration_objects = s3.list_objects_v2(Bucket=bucketName, Prefix=registration_prefix)
    registration_count = len(registration_objects.get('Contents', []))

    # Contagem de validações
    audit_prefix = f'name_folder/{userId}/' # Replace with your prefix
    audit_objects = s3.list_objects_v2(Bucket=bucketName, Prefix=audit_prefix)
    audit_count = len(audit_objects.get('Contents', []))

    return registration_count, audit_count
