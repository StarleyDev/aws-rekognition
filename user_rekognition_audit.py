# Description: Detect faces in an image and compare them with a target image
# Event: user_rekognition_audit
# Author: Starley Cazorla
# Version: 1.0
# Language: python
# Runtime: python3.7
# License: MIT


import boto3
import json
import botocore.exceptions

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1') # Replace with your AWS Region
dynamodbTableName = 'name-of-your-dynamodb-table' # Replace with your DynamoDB table name
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') # Replace with your AWS Region
userTable = dynamodb.Table(dynamodbTableName)
bucketName = 'your-bucket' # Replace with your S3 bucket name

def lambda_handler(event, context):
  idPerson = event['queryStringParameters']['userId']
  hashKey = event['queryStringParameters']['hashKey']

  target_file = f'name_folder/{idPerson}/{hashKey}.jpg' # Replace with your target file name
  prefix = f'name_folder/{idPerson}/' # Replace with your prefix
  source_file = list_sources_files(prefix)

  for file in source_file:
    print(file)
    face_matches = compare_faces(file, target_file)
    print("Face matches: ", face_matches)

    if isinstance(face_matches, str):
            # Se compare_faces retornar uma string, trate como um erro
            return buildResponse(200, {
                'message': 'A imagem enviada não corresponde a um rosto!',
                'status': 404
            })

    if face_matches:
      if face_matches['Similarity'] > 80:

          scan_result = userTable.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('userId').eq(idPerson)
          )

          if scan_result['Items']:
              face = scan_result['Items'][0] # Assume the first match is the correct one
              print('Person found in database', face)
              return buildResponse(200, {
                  'message': 'Encontramos a seguinte pessoa!',
                  'userName': face['userName'],
                  'userId': face['userId'],
                  'similarity': face_matches['Similarity'],
                  'status': 200
              })
          # If no matches in the database, return not found after checking all FaceMatches
          return buildResponse(200, {
              'message': 'Não conseguimos te encontrar na base de dados!'
          })
      else:
          # If no FaceMatches at all, return not found
          return buildResponse(200, {
              'message': 'Pessoa encontrada porem a similaridade e inferior a desejada!',
              'status': 404
          })
    else:
        continue
  # If the loop completes without finding a match, return not found
  return buildResponse(200, {
    'message': 'Não conseguimos te encontrar na base de dados!',
    'status': 404
  })

# Compare faces
def compare_faces(sourceFile, targetFile):
    try:
        response = rekognition.compare_faces(SimilarityThreshold=80,
                                             SourceImage={'S3Object': {'Bucket': bucketName, 'Name': sourceFile}},
                                             TargetImage={'S3Object': {'Bucket': bucketName, 'Name': targetFile}})

        if response.get('FaceMatches'):
            for faceMatch in response['FaceMatches']:
                position = faceMatch['Face']['BoundingBox']
                similarity = str(faceMatch['Similarity'])
                print('The face at ' +
                      str(position['Left']) + ' ' +
                      str(position['Top']) +
                      ' matches with ' + similarity + '% confidence')

            return faceMatch
        else:
            print('No face matches found.')
            return None
    except botocore.exceptions.ClientError as e:
        error_message = e.response.get('Error', {}).get('Message', 'Unknown error occurred')
        print('Error: ', error_message)
        return error_message

# Get list of objects by prefix (user)
def list_sources_files(prefix):
    response = s3.list_objects_v2(Bucket=bucketName, Prefix=prefix)
    #return [object['Key'] for object in response.get('Contents', []) if '_Back' not in object['Key']]
    objects = response.get('Contents', [])

    # Sort the objects so that files containing '_Selfie' come first
    objects.sort(key=lambda obj: '_Selfie' not in obj['Key'])

    return [object['Key'] for object in objects if '_Back' not in object['Key']]

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
