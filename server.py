from flask import Flask
from flask import render_template, redirect, url_for
from flask_socketio import SocketIO, emit, send

from users import *

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("template.html")

@app.route("/register_login/")
def register_login():
    return render_template("register_login.html")

# handle user registration
@socketio.on("register_user")
def register_user(data):
    print("ASDFASDFASDF")
    # extract data from socket event    
    email = data["email"]
    username = data["username"]
    password = data["password"]
    confirmPassword = data["confirmPassword"]
    # did registration work
    registration_succeeded, new_user_object = User.register(email, username, password)
    # emit event if failed
    if (registration_succeeded): 
        emit("registration_failed", {"details": "email already used"})
    else:
        emit("registration_failed", {"details": "email already used"})

@app.route("/homepage/")
def homepage():
    return render_template("homepage.html")

socketio.run(app, host = "0.0.0.0", port = 8080, debug = True)

