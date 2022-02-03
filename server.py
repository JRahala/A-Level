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

# create new placement using the placement form in homepage
@socketio.on("createPlacementForm")
def create_placement_form(data):
    
    # extract user object from session
    user_object = User.database[session["user_key"]]

    # retrieve placement data to check if all fields properly filled in 
    title = data["placementTitle"]
    description = data["placementDescription"]
    start_date = data["placementStartDate"]
    end_date = data["placementEndDate"]
    subject_tags = data["placementSubjectTags"]
    location_tag = data["placementLocationTag"]

    # parse data input and create date range object
    start_year, start_month, start_day = start_date.split("-")
    start_date = Date(
        int(start_day),
        int(start_month),
        int(start_year)
    )

    end_year, end_month, end_day = end_date.split("-")
    end_date = Date(
        int(end_day),
        int(end_month),
        int(end_year)
    )

    date_range = DateRange(start_date, end_date)
        
    # create subject tag object(s)
    subject_tags = [SubjectTag(subject_tag) for subject_tag in subject_tags]

    # create location tag object
    location_tag = LocationTag(location_tag)
    
    # try to create placement using the data object
    successful, new_placement_object = user_object.create_new_placement(title, description, date_range, location_tag, subject_tags)
    if not (successful):
        emit("placementFormAlert", {"successful": False, "message": "placement name already used"})
    
    else:
        # refresh page on placement creation
        emit("placementFormAlert", {"successful": True, "message": "placement succesfully created"})
        emit("refreshEvent")

@socketio.on("editPlacementForm")
def edit_placement_form(data):

    # extract user object from session
    user_object = User.database[session["user_key"]]

    # retrieve placement data to check if all fields properly filled in 
    title = data["placementTitle"]
    description = data["placementDescription"]
    start_date = data["placementStartDate"]
    end_date = data["placementEndDate"]
    subject_tags = data["placementSubjectTags"]
    location_tag = data["placementLocationTag"]

    # parse data input and create date range object
    start_year, start_month, start_day = start_date.split("-")
    start_date = Date(
        int(start_day),
        int(start_month),
        int(start_year)
    )

    end_year, end_month, end_day = end_date.split("-")
    end_date = Date(
        int(end_day),
        int(end_month),
        int(end_year)
    )

    date_range = DateRange(start_date, end_date)
        
    # create subject tag object(s)
    subject_tags = [SubjectTag(subject_tag) for subject_tag in subject_tags]

    # create location tag object
    location_tag = LocationTag(location_tag)
    
    # try to create placement using the data object
    successful, new_placement_object = user_object.edit_placement(title, description, date_range, location_tag, subject_tags)
    if not (successful):
        emit("placementFormAlert", {"successful": False, "message": "placement does not exist"})
    
    else:
        # refresh the page when placement successfully edited
        emit("placementFormAlert", {"successful": True, "message": "placement succesfully edited"})
        emit("refreshEvent")


@socketio.on("deletePlacementForm")
def delete_placement_form(placement_title):

    # extract user object from session
    user_object = User.database[session["user_key"]]

    # attempt to delete placement 
    user_object.delete_placement(placement_title)

    # refresh the page event
    emit("refreshEvent")

socketio.run(app, host = "0.0.0.0", port = 8080, debug = True)

