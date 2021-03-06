#encoding: utf-8

from datetime import datetime
import json

from flask import make_response, current_app
from flask_jwt import JWT, jwt_required, current_identity

jwt_auth = JWT()

@jwt_auth.jwt_error_handler
def jwt_error(e):
    import json
    return make_response(json.dumps({"msg": str(e)}), 401)

@jwt_auth.jwt_payload_handler
def jwt_payload_handler(user_info):
    iat = datetime.utcnow()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
    return {
        'exp': exp,
        'iat': iat,
        'nbf': nbf,
        "user": user_info.get("user"),
        "current_account": user_info.get("current_account"),
    }

@jwt_auth.identity_handler
def jwt_identity(payload):
    return {"email": payload.get("email")}



def jwt_generate_user_info(user, current_account):
    return {
        "user": {
            "email": user.tx_email,
            "name": user.tx_name
        },
        "current_account": {
            "id": current_account.id,
            "name": current_account.name,
            "namespace": current_account.namespace
        }
    }
