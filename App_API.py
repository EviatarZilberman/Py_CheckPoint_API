from flask import Flask, request, jsonify
from DataModels.PaymentDetails import PaymentDetails
from DataModels.PersonalDetails import PersonalDetails
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
    payment_data = data["form"]
    correct_payment_id = PaymentDetails.details_validation(payment_data)
    if len(correct_payment_id) > 0:
        return jsonify(correct_payment_id), 400
    user_id = data["user_id"]

    db_manager = MongoDbSingleton.MongoDbSingleton("E_Commerce", "Users")
    dictionary = db_manager.find_one_by_key_value("_id", user_id)

    payment_instance = PaymentDetails.from_dict(payment_data)
    sent_password = dictionary["password"]
    if sent_password == payment_data["password"]:
        try:
            db_manager.update_member(user_id, 'personal_details.payment_details', payment_instance)
            return jsonify(), 200
        except:
            user = User.from_dict(dictionary)
            if not user.m_personal_details:
                user.m_personal_details = PersonalDetails()
                user.m_personal_details.m_payment_details = payment_instance
            else:
                user.m_personal_details.m_payment_details = payment_instance

        db_manager.replace_member(user)
        return jsonify(), 200
    else:
        jsonify(), 409


@app_api.route("/edit_address", methods = ['POST'])
def edit_address():
    pass

if __name__ == "__main__":
    app_api.run(port = 9998, debug = True)