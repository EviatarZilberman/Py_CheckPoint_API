from flask import Flask, request, jsonify
from DataModels.Address import Address
from DataModels.PaymentDetails import PaymentDetails
from DataModels.PersonalDetails import PersonalDetails
from DataModels.User import User
from Enums.LogLevels import LogLevel
from MongoDbManager.MongoDbSingleton import MongoDbSingleton
from Models.Writer import Writer

app_api = Flask(__name__)
path = r'C:\Users\User\Projects\Logs'
log_file = 'CheckPoint_Logs.log'


@app_api.route("/register", methods = ["POST"])
def register():
    from DataModels.User import User

    errors = []
    data = request.get_json()
    username = data["username"]
    f_name = data["f_name"]
    l_name = data["l_name"]
    email = data["email"]
    password = data["password"]
    confirm_password = data["confirm_password"]

    try:
        user = MongoDbSingleton("E_Commerce", "Users").find_by_key_value("email", email)
    except Exception as e:
        return None

    if user:
        errors.append("User is already exist!")
        return jsonify(errors), 409

    errors = User.valid_password(password, confirm_password)
    if errors:
        return jsonify(errors), 409

    try:
        MongoDbSingleton.reinitialize()
        MongoDbSingleton("E_Commerce", "Users").insert(User(username, f_name, l_name, email, password))
    except Exception as e:
        print(str(e))
        return None

    return jsonify(["User created successfully!"]), 201


@app_api.route("/login", methods = ["POST", "GET"])
def login():
    data = request.get_json()
    username_or_email = data["username_or_email"]
    password = data["password"]
    stay_logged = data.get("stay_logged")

    MongoDbSingleton.reinitialize()
    try:
        dictionary = MongoDbSingleton('E_Commerce', 'Users').find_one_by_key_value("email", username_or_email)
    except Exception as e:
        print(str(e))
        return None
    if not dictionary:
        MongoDbSingleton.reinitialize()
        dictionary = MongoDbSingleton('E_Commerce', 'Users').find_one_by_key_value("username", username_or_email)

    if not dictionary:
        return jsonify(["Username or email not found!"]), 404

    from DataModels.User import User
    user = User.from_dict(dictionary)
    if password == user.password:
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
    user_id = data["user_id"]

    MongoDbSingleton.reinitialize()
    dictionary = MongoDbSingleton('E_Commerce', 'Users').find_one_by_key_value("_id", user_id)
    user = User.from_dict(dictionary)
    payment_instance = PaymentDetails.from_dict(payment_data)
    sent_password = dictionary["password"]
    if sent_password == payment_data["password"]:
        try:
            if user.personal_details and user.personal_details.payment_details is None:
                user.personal_details = PersonalDetails()
                user.personal_details.payment_details = PaymentDetails()
                user.personal_details.payment_details = payment_instance
                MongoDbSingleton('E_Commerce', 'Users').replace_member(user)
                return jsonify(), 200
            elif user.personal_details is not None and user.personal_details.payment_details is None:
                user.personal_details.payment_details = PaymentDetails()
                user.personal_details.payment_details = payment_instance
                MongoDbSingleton('E_Commerce', 'Users').replace_member(user)
                return jsonify(), 200
            else:
                # db_manager.update_member(user_id, 'personal_details.payment_details', payment_instance)
                user.personal_details.payment_details = PaymentDetails()
                user.personal_details.payment_details = payment_instance
                MongoDbSingleton('E_Commerce', 'Users').replace_member(user)
                return jsonify(), 200
        # try:
        #     db_manager.update_member(user_id, 'personal_details.payment_details', payment_instance)
        #     return jsonify(), 200
        except:
            user = User.from_dict(dictionary)
            if not user.personal_details:
                user.personal_details = PersonalDetails()
                user.personal_details.payment_details = payment_instance
            else:
                user.personal_details.payment_details = payment_instance

            MongoDbSingleton('E_Commerce', 'Users').replace_member(user)
            return jsonify(), 200
    else:
        jsonify(), 409


@app_api.route("/edit_personal_details", methods = ['POST'])
def edit_personal_details():
    data = request.get_json()
    personal_data = data["form"]
    user_id = data["user_id"]
    MongoDbSingleton.reinitialize()
    dictionary = MongoDbSingleton('E_Commerce', 'Users').find_one_by_key_value("_id", user_id)
    user = User.from_dict(dictionary)
    address_instance = Address.from_dict(personal_data)
    try:
        if user.personal_details and user.personal_details.address is None:
            MongoDbSingleton('E_Commerce', 'Users').update_member(user_id, 'personal_details.address', address_instance)
            return jsonify(), 200
        elif user.personal_details and user.personal_details.address:
            MongoDbSingleton('E_Commerce', 'Users').update_member(user_id, 'personal_details.address', address_instance)
            return jsonify(), 200
        else:
            item_id = None
            if 'entrance' in dictionary:
                entrance = dictionary["entrance"]
            else:
                entrance = None
            if 'mail_box' in dictionary:
                mail_box = dictionary["mail_box"]
            else:
                mail_box = None
            if 'id' in dictionary:
                item_id = dictionary["id"]
            else:
                mail_box = None
            if 'created_at' in dictionary:
                created_at = dictionary["created_at"]
            else:
                created_at = None
            user.m_personal_details.m_address = Address(personal_data['country'], personal_data['city'],
                                                        personal_data['street'], personal_data['number'],
                                                        personal_data['floor'], personal_data['apartment'],
                                                        entrance, mail_box, item_id, created_at)
        MongoDbSingleton('E_Commerce', 'Users').replace_member(user)
        return jsonify(), 200
    except Exception as e:
        print(str(e))
        if not user.personal_details:
            user.personal_details = PersonalDetails()
            user.personal_details.address = address_instance
        else:
            user.personal_details.address = address_instance

    MongoDbSingleton('E_Commerce', 'Users').replace_member(user)
    return jsonify(), 200


@app_api.route('/change_password', methods = ['POST'])
def change_password():
    data = request.get_json()
    user_id = data["user_id"]
    form = data['form']
    old_password = form['old_password']
    new_password = form['new_password']
    confirm_new_password = form['confirm_new_password']

    MongoDbSingleton.reinitialize()
    dictionary = MongoDbSingleton('E_Commerce', 'Users').find_one_by_key_value("_id", user_id)
    dict_old_password = dictionary["password"]
    if dict_old_password != old_password:
        return jsonify(), 409
    else:
        error_list = User.valid_password(new_password, confirm_new_password)
        if len(error_list) == 0:
            try:
                user = User.from_dict(dictionary)
                user.password = new_password
                MongoDbSingleton('E_Commerce', 'Users').replace_member(user)
                # db_manager.update_member(user_id, 'password', new_password)
                return jsonify(), 200
            except:
                user = User.from_dict(dictionary)
                user.password = new_password
                MongoDbSingleton('E_Commerce', 'Users').replace_member(user)

                return jsonify(), 200
        else:
            jsonify(), 409


@app_api.route("/return_personal_details", methods = ["POST"])
def return_personal_details():
    data = request.get_json()
    user_id = data['user_id']

    from DataModels.User import User
    try:
        user = User.from_dict(MongoDbSingleton('E_Commerce', 'Users').find_by_id(user_id))
    except Exception as e:
        Writer(path=path, file_name=log_file).write_log(str(e), level=LogLevel.ERROR)
        return jsonify(), 404
    if not user:
        return jsonify(), 404

    result = user.personal_details

    return jsonify(result), 200


if __name__ == "__main__":
    app_api.run(port = 9998, debug = True)