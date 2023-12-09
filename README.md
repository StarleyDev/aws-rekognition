# AWS Rekognition with Lambda Functions

This repository contains a collection of Lambda functions for integrating with AWS Rekognition for various user management tasks such as authorization, existence check, registration, and recognition.

#### Installation Instructions

1. **Prepare the Lambda Package:**

   - Compress the 'token' folder and necessary `node_modules` into a zip file.

2. **Lambda Deployment:**

   - Upload the zip file to your Lambda function.

3. **Run pip install (for local development test):**
   - pip install -r requirements.txt

#### Configuration

- Add `accountId` and `apiGatewayId` in the `user_authorization_token.ts`.
- Set the `secretKey`.

## Functions

### User Authorization Token (`user_authorization_token.ts`)

This function is responsible for authorizing users to access specified resources.

### User Check Existence (`user_check_exist.py`)

This function checks whether a user exists in the database. If a `hashKey` is passed, it further checks for a rekognition record associated with the user.

### User Registration (`user_registration.py`)

This function handles user registration. It uploads an image to an S3 bucket and saves user data in the database. This function can also update the image in case the user sends a new image to rekognition.

### User Recognition (`user_recognition.py`)

This function processes an image through rekognition and returns the analysis. It outputs both the rekognition result and associated user data.

## Authors

- [@StarleyDev](https://github.com/StarleyDev)
