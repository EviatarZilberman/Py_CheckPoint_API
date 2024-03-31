import base64
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response

import Global_methods
from MongoDbManager import MongoDbSingleton
from Enums.CookiesClaims import CookiesClaims
from os import environ
from cryptography.fernet import Fernet
from dotenv import load_dotenv


app_api = Flask(__name__)
load_dotenv()


@app_api.route("/register", methods = ["POST"])
def register():
    from DataModels.User import User

    db_manager = MongoDbSingleton.MongoDbSingleton("E_Commerce", "Users")
    errors = []
    data = request.get_json()
    username = data["username"]
    f_name = data["f_name"]
    l_name = data["l_name"]
    email = data["email"]
    password = data["password"]
    confirm_password = data["confirm_password"]

    user = db_manager.find_by_key_value("email", email)
    if user:
        errors.append("User is already exist!")
        return jsonify(errors), 409

    errors = User.valid_password(password, confirm_password)
    if errors:
        return jsonify(errors), 409

    # key_bytes = Global_methods.string_to_urlsafe_base64_bytes(email)
    # cipher = Fernet(key_bytes)
    # encrypted_password = cipher.encrypt(password.encode())
    db_manager.m_instance.insert(User(username, f_name, l_name, email, password))

    return jsonify(["User created successfully!"]), 201


@app_api.route("/login", methods = ["POST"])
def login():
    data = request.get_json()
    username_or_email = data["username_or_email"]
    password = data["password"]
    stay_logged = data.get("stay_logged")

    db_manager = MongoDbSingleton.MongoDbSingleton("E_Commerce", "Users")
    dictionary = db_manager.find_one_by_key_value("email", username_or_email)
    if not dictionary:
        dictionary = db_manager.find_one_by_key_value("username", username_or_email)

    if not dictionary:
        return jsonify(["Username or email not found!"]), 404

    from DataModels.User import User
    user = User.from_dict(dictionary)
    if password == user.m_password:
        # claims = list()
        # claims.append(str(CookiesClaims.USERNAME))
        # claims.append(str(CookiesClaims.EMAIL))
        # parameters = list()
        # parameters.append(user.m_username)
        # parameters.append(user.m_email)
        # if not stay_logged:
        #     expiration_time = datetime.now() + timedelta(minutes = int(environ.get('EXPIRATION_TIME_DEFAULT_MINUTES')))
        # else:
        #     expiration_time = datetime.now() + timedelta(days = int(environ.get('EXPIRATION_TIME_PERSIST_DAYS')))
        #     claims.append(str(CookiesClaims.IS_PERSIST))
        #     parameters.append(str(stay_logged))
        #
        # expires_timestamp = expiration_time.timestamp()
        # response = make_response()
        # for claim, parameter in zip(claims, parameters):
        #     response.set_cookie(str(claim), str(parameter), expires=expires_timestamp)
        result = {
            'user': user.to_dict(),
            'stay_logged': stay_logged
        }

        return jsonify(result), 200

    return jsonify(["Not matched username, email or password!"]), 401


# @app_api.route("/already_logged", methods = ["POST"])
# def already_logged():
#     data = request.get_json()
#     email = data["email"]
#     db_manager = MongoDbSingleton.MongoDbSingleton("E_Commerce", "Users")
#     user_dict = db_manager.find_one_by_key_value("email", email)
#     return jsonify(user_dict), 200


if __name__ == "__main__":
    app_api.run(port = 9998, debug = True)