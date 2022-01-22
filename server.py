from flask import Flask
from flask import render_template, redirect, url_for, session
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
    
    # extract data from socket event    
    email = data["email"]
    username = data["username"]
    password = data["password"]
    confirmPassword = data["confirmPassword"]
    isStudent = data["isStudent"]

    # check if password and confirmedPassword are the same
    if (password != confirmPassword):
        emit("reglog_failed", {"details": "passwords do not match"})
        return

    # check if password is long enough
    if len(password) < 10:
        emit("reglog_failed", {"details": "password must contain at least 10 characters"})
        return

    # check if password contains complex chars
    contains_complex_char = False
    for char in password:
        if char in "!£$%^&*()":
            contains_complex_char = True

    if contains_complex_char == False:
        emit("reglog_failed", {"details": "password does not contain complex character !£$%^&*()"})
        return 

    # check for valid email
    if (not "@" in email):
        emit("reglog_failed", {"details": "invalid email supplied"})
        return 
    
    # did registration work
    registration_succeeded, new_user_object = User.register(email, username, password, isStudent)

    # emit event if failed
    if (registration_succeeded): 
        # save user object into session for later use
        session["user_object"] = new_user_object
        emit("reglog_succeeded")
    else:
        emit("reglog_failed", {"details": "email already used"})

@socketio.on("login_user")
# handle user login
def login_user(data):

    # extract data from socket event
    email = data["email"]
    password = data["password"]

    logged_in_successfully, user_object = User.login(email, password)
    if (logged_in_successfully):
        # save user object into session for later use
        session["user_object"] = user_object
        emit("reglog_succeeded")
        print("LOGGED IN!")
    else:
        print("ASDFSD")
        emit ("reglog_failed", {"details": "email or password incorrect"})


@app.route("/homepage/")
def homepage():
    return render_template("homepage.html")

socketio.run(app, host = "0.0.0.0", port = 8080, debug = True)

