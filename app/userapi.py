"""Code to Create, Read, Update, Delete users"""
import os
from flask import jsonify, request, Flask
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config["MYSQL_DATABASE_USER"] = os.getenv("MYSQL_DATABASE_USER")
app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_DATABASE_PASSWORD")
app.config["MYSQL_DATABASE_DB"] = os.getenv("MYSQL_DATABASE_DB")
app.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_DATABASE_HOST")
app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("MYSQL_DATABASE_PORT"))
mysql.init_app(app)


@app.route("/")
def index():
    """Home page of the API"""
    return "Hi :D "


@app.route("/create_table")
def create_table():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        create_table_query = """
            CREATE TABLE users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(255) NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                user_password VARCHAR(255) NOT NULL
            )
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        return "Table 'users' created successfully!"
    except Exception as e:
        return str(e)


@app.route("/create", methods=["POST"])
def add_user():
    """Function to create a user to the MySQL database"""
    json = request.json
    name = json["name"]
    email = json["email"]
    pwd = json["pwd"]
    if name and email and pwd and request.method == "POST":
        sql = "INSERT INTO users(user_name, user_email, user_password) " \
              "VALUES(%s, %s, %s)"
        data = (name, email, pwd)
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            cursor.close()
            conn.close()
            resp = jsonify("User created successfully!")
            resp.status_code = 200
            return resp
        except Exception as exception:
            return jsonify(str(exception))
    else:
        return jsonify("Please provide name, email and pwd")


@app.route("/users", methods=["GET"])
def users():
    """Function to retrieve all users from the MySQL database"""
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as exception:
        return jsonify(str(exception))


@app.route("/user/<int:user_id>", methods=["GET"])
def user(user_id):
    """Function to get information of a specific user in the MSQL database"""
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=%s", user_id)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as exception:
        return jsonify(str(exception))


@app.route("/update", methods=["POST"])
def update_user():
    """Function to update a user in the MYSQL database"""
    json = request.json
    name = json["name"]
    email = json["email"]
    pwd = json["pwd"]
    user_id = json["user_id"]
    if name and email and pwd and user_id and request.method == "POST":
        # save edits
        sql = "UPDATE users SET user_name=%s, user_email=%s, " \
              "user_password=%s WHERE user_id=%s"
        data = (name, email, pwd, user_id)
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            resp = jsonify("User updated successfully!")
            resp.status_code = 200
            cursor.close()
            conn.close()
            return resp
        except Exception as exception:
            return jsonify(str(exception))
    else:
        return jsonify("Please provide id, name, email and pwd")


@app.route("/delete/<int:user_id>")
def delete_user(user_id):
    """Function to delete a user from the MySQL database"""
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=%s", user_id)
        conn.commit()
        cursor.close()
        conn.close()
        resp = jsonify("User deleted successfully!")
        resp.status_code = 200
        return resp
    except Exception as exception:
        return jsonify(str(exception))


if __name__ == "__main__":
    listen_addr = os.getenv("APP_LISTEN_ADDRESS", "0.0.0.0")
    listen_port = int(os.getenv("APP_LISTEN_PORT", 5000))
    app.run(host=listen_addr, port=listen_port)
