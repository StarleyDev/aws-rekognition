// Description: User authorization token
// Event: user_authorization_token
// Author: Starley Cazorla
// Version: 1.0
// License: MIT

const CryptoJS = require("crypto-js");
const secretKey = "1234567890123456"; // Your secret key

const acountID = "ACOUNTID"; // Your aws account ID
const apiGetwayID = "GETWAYID"; // Your API getway ID

export const handler = async (event) => {
    // TODO implement
    let token = event['authorizationToken'];

    token = decryptToken(token);

    let permission = "Deny";
    if (token === "yourToken") {
        permission = "Allow";
    }

    const authReponse = {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": permission,
                    "Resource": [`arn:aws:execute-api:us-east-1:${acountID}:${apiGetwayID}/**`],
                }
            ]
        }
    };

    return authReponse;
};

function decryptToken(token) {
    return CryptoJS.AES.decrypt(token, secretKey).toString(CryptoJS.enc.Utf8);
}


// For criptography your token, you can use this function to encrypt your token in client side.

// encrypt(data: any) {
//     const payload = {
//         data: data,
//         timestamp: new Date().getTime()
//     }
//     const ciphertext = CryptoJS.AES.encrypt(JSON.stringify(payload), secretKey).toString();
//     return ciphertext;
// }
