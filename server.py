from flask import Flask
from flask import render_template, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit, send
from flask_session import Session
from users import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "top_secret"         # secret key used for encryption purposes (will be changed after development)
app.config["SESSION_TYPE"] = "filesystem"       # use flask session
sess = Session(app)                             # use server side sessions
socketio = SocketIO(app, manage_session=False)  # flask_socketio session uses flask session

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
    registration_succeeded, new_user_object, new_user_key = User.register(email, username, password, isStudent)

    # emit event if failed
    if (registration_succeeded): 
        # save user object key into session for later use
        session["user_key"] = new_user_key
        emit("reglog_succeeded")
    else:
        emit("reglog_failed", {"details": "email already used"})

@socketio.on("login_user")
# handle user login
def login_user(data):

    # extract data from socket event
    email = data["email"]
    password = data["password"]

    logged_in_successfully, user_object, user_key = User.login(email, password)
    if (logged_in_successfully):
        # save user object key into session for later use
        session["user_key"] = user_key
        emit("reglog_succeeded")
    else:
        emit ("reglog_failed", {"details": "email or password incorrect"})


@app.route("/homepage/")
def homepage():
    # AUTOMATED!
    _, user_object, user_key = User.register("rahala.j@etoncollege.org.uk", "Jasamrit", "Password123!", False)

    user_object.create_new_placement(
        title = "Mathematics Placement", 
        description = "This placement is to do with maths and data science",
        date_range = DateRange(
            start_date = Date(1,1,1),
            end_date = Date(2,3,1)
        ),
        location_tag = LocationTag("Berkshire"),
        subject_tags = [SubjectTag("Mathematics"), SubjectTag("Data"), SubjectTag("Excel")]
    )

    user_object.create_new_placement(
        title = "1234", 
        description = "^%$£",
        date_range = DateRange(
            start_date = Date(1,1,1),
            end_date = Date(1,1,99)
        ),
        location_tag = LocationTag("Oxfordshire"),
        subject_tags = []
    )

    session["user_key"] = user_key
    return render_template("homepage.html")

# return the users username
@socketio.on("getUserUsername")
def get_user_username():
    # retrieve user object
    user_object = User.database[session["user_key"]]
    emit("returnUserUsername", user_object.username)

# return the current users placements
@socketio.on("getUserPlacements")
def get_user_placements():
    # retrieve user object
    user_object = User.database[session["user_key"]]
    emit("returnUserPlacements", [user_object.placements[placement_title].json_summary() for placement_title in user_object.placements])

socketio.run(app, host = "0.0.0.0", port = 8080, debug = True)

