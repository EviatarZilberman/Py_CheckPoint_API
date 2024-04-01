from flask import Flask, request, jsonify
from MongoDbManager import MongoDbSingleton
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
        result = {
            'user': user.to_dict(),
            'stay_logged': stay_logged
        }

        return jsonify(result), 200

    return jsonify(["Not matched username, email or password!"]), 401


@app_api.route("/edit_payment_details", methods = ['POST'])
def edit_payment_details():
    data = request.get_json()
    username_or_email = data["username_or_email"]
    password = data["password"]
    stay_logged = data.get("stay_logged")

    db_manager = MongoDbSingleton.MongoDbSingleton("E_Commerce", "Users")
    dictionary = db_manager.find_one_by_key_value("email", username_or_email)


if __name__ == "__main__":
    app_api.run(port = 9998, debug = True)