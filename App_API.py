from flask import Flask, request, jsonify
from DataModels.PaymentDetails import PaymentDetails
from DataModels.User import User
from MongoDbManager import MongoDbSingleton

app_api = Flask(__name__)


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
    try:
        data = request.get_json()
    except Exception as e:
        print(str(e))
    try:
        payment_data = data["form"]
    except Exception as e:
        print(str(e))
    correct_payment_id = PaymentDetails.details_validation(payment_data)
    if not correct_payment_id:
        return 400
    user_id = data["user_id"]

    db_manager = MongoDbSingleton.MongoDbSingleton("E_Commerce", "Users")
    dictionary = db_manager.find_one_by_key_value("_id", user_id)

    payment_instance = PaymentDetails.from_dict(dictionary)
    try:
        db_manager.update_member(user_id, 'payment_details', payment_instance)
        return 200
    except:
        user = User.from_dict(dictionary)
        user.m_payment_details = payment_instance
        db_manager.replace_member(user)
        return 200


if __name__ == "__main__":
    app_api.run(port = 9998, debug = True)