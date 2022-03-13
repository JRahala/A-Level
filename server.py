from flask import Flask
from flask import render_template, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit, send
from flask_session import Session
from torch import true_divide
from users import *
from datetime import datetime # provide date functionality

app = Flask(__name__)
app.config["SECRET_KEY"] = "top_secret"         # secret key used for encryption purposes (will be changed after development)
app.config["SESSION_TYPE"] = "filesystem"       # use flask session
sess = Session(app)                             # use server side sessions
socketio = SocketIO(app, manage_session=False)  # flask_socketio session uses flask session

# direct user to landing page
@app.route("/")
def index():
    return render_template("template.html")

# direct user to register / login page
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

# direct user to homepage
@app.route("/homepage/")
def homepage():
    return render_template("homepage.html")

# is the user a student?
@socketio.on("isStudent")
def is_student():
    # retrieve user object
    user_object = User.database[session["user_key"]]
    if isinstance(user_object, Student):
        emit("recieveStudent", True)
    else:
        emit("recieveStudent", False)

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

    # date input properly filled in?
    if len(start_date.split("-")) != 3:
        emit("placementFormAlert", {"successful": False, "message": " start date not filled in"})
    
    if len(end_date.split("-")) != 3:
        emit("placementFormAlert", {"successful": False, "message": " end date not filled in"})

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
        emit("placementFormAlert", {"successful": False, "message": " placement name already used"})
    
    else:
        # refresh page on placement creation
        emit("placementFormAlert", {"successful": True, "message": " placement succesfully created"})
        emit("refreshEvent")

# edit the placement from the homepage form
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

    # remove any duplicates
    subject_tags = set(subject_tags)
    subject_tags = [x for x in subject_tags]

    # date input properly filled in?
    if len(start_date.split("-")) != 3:
        emit("placementFormAlert", {"successful": False, "message": " start date not filled in"})
    
    if len(end_date.split("-")) != 3:
        emit("placementFormAlert", {"successful": False, "message": " end date not filled in"})

    # parse data input and create date range object (take the last two digits for the year)
    start_year, start_month, start_day = start_date.split("-")
    start_date = Date(
        int(start_day),
        int(start_month),
        int(start_year[-2] + start_year[-1])
    )

    end_year, end_month, end_day = end_date.split("-")
    end_date = Date(
        int(end_day),
        int(end_month),
        int(end_year[-2] + end_year[-1])
    )

    date_range = DateRange(start_date, end_date)
        
    # create subject tag object(s)
    subject_tags = [SubjectTag(subject_tag) for subject_tag in subject_tags]

    # create location tag object
    location_tag = LocationTag(location_tag)
    
    # try to create placement using the data object
    successful, new_placement_object = user_object.edit_placement(title, description, date_range, location_tag, subject_tags)
    print(title, description, date_range, location_tag, subject_tags)

    if not (successful):
        emit("placementFormAlert", {"successful": False, "message": " placement does not exist"})
    
    else:
        # refresh the page when placement successfully edited
        emit("placementFormAlert", {"successful": True, "message": " placement succesfully edited"})
        emit("refreshEvent")

# delete the placement from the homepage form
@socketio.on("deletePlacementForm")
def delete_placement_form(placement_title):

    # extract user object from session
    user_object = User.database[session["user_key"]]

    # attempt to delete placement 
    user_object.delete_placement(placement_title)

    # refresh the page event
    emit("refreshEvent")

# save placement to saved_placements
@socketio.on("savePlacement")
def save_placement(data):

    # extract user object from session
    user_object = User.database[session["user_key"]]

    # extract placement_title and company name to save to user_object
    placement_title = data["placementTitle"]
    company_name = data["placementCompanyName"]

    # save placement to user_object
    user_object.save_placement(company_name, placement_title)

# navigate to saved placements websites
@app.route("/saved_placements/")
def saved_placements():
    return render_template("saved_placements.html")

# return array of placement.json_summary for saved placements
@socketio.on("retrieveSavedPlacements")
def retrieve_saved_placements():
    
    # extract user object from session
    user_object = User.database[session["user_key"]]

    # get the array of the user stack of saved_placements
    saved_placements_array = user_object.saved_placements.array_copy()
    saved_placements_json = [placement.json_summary() for placement in saved_placements_array]

    # let the client know to display the returned results
    emit("displaySavedPlacements", {"placementsArray": saved_placements_json})

# navigate to search page 
@app.route("/search/")
def search_placements():
    return render_template("search.html")

# return array of subject tags 
@socketio.on("getSubjectTags")
def get_subject_tags():
    subject_tag_list = [subject_tag.json_summary() for subject_tag in SubjectTag.all_subject_tags]
    # emit the event here for the tags to load as datalist elements
    emit("loadSubjectTagSearchbar", subject_tag_list)

# return array of location tags
@socketio.on("getLocationTags")
def get_location_tags():
    location_tag_list = [location_tag for location_tag in LocationTag.distance_dictionary]
    # emit the event here for the tags to load as datalist elements
    emit("loadLocationTagSearchbar", location_tag_list)

# return search placements
@socketio.on("searchPlacements")
def search_placements(data):

    # use the placement trie
    subject_tags = sorted(data["subjectTags"]) # for placement trie
    location_tag = data["locationTag"]
    location_range = data["locationRange"]
    start_date = data["startDate"]
    end_date = data["endDate"]

    # recast subject_tag strings into subject tags
    subject_tags = [SubjectTag(subject_tag_string) for subject_tag_string in subject_tags]
    
    # search on placement.subject_trie using subject_tags
    valid_placements = Placement.dirty_search_subject_trie(subject_tags)
    Placement.subject_trie.peek()

    # create location tag
    if location_tag == "" or location_range == "" or location_range == "0":
        # no location provides => location spans everywhere
        location_tag = LocationTag("London")
        location_range = 9999999999
    else:
        location_tag = LocationTag(location_tag)
        location_range = int(location_range)

    # create date range tag
    if start_date == "" or end_date == "" or len(start_date.split("-")) != 3 or len(end_date.split("-")) != 3:
        # no valid date provides => date range spans 100 years
        date_range = DateRange(Date(1,1,1), Date(31, 12, 100))
    else:
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

    # return filtered placements
    valid_placements = Placement.filter_placements(valid_placements, date_range, location_tag, location_range)

    # return json summaries
    emit("searchResponse", [placement.json_summary() for placement in valid_placements]) 

# student applies to placement
@socketio.on("applyPlacement")
def apply_placement(data):
    
    # extract user object from session
    user_object = User.database[session["user_key"]]

    # retrieve placement title and company name 
    placement_title = data["placementTitle"]
    company_name = data["placementCompanyName"]
    company_object = Company.name_to_object[company_name]
    # get placement from Placement.global_placements dictionary
    current_placement = Placement.global_placements[(company_name, placement_title)]

    # add student to placement students
    current_placement.applied_students.add(user_object)

    # add placement to student applied_placements stack
    user_object.applied_placements.push(current_placement)

    # add notifications
    user_object.notifications_stack.push(["Applied to '" + placement_title + "'", "Application", datetime.today().strftime("%Y-%m-%d"), "You applied to the placement '" + placement_title + "' offered by company '" + company_name + "'"])
    company_object.notifications_stack.push(["User applied to '" + placement_title + "'", "Application", datetime.today().strftime("%Y-%m-%d"), "User signed up to placement '" + placement_title + "'"])


# create a message group from the students who have applied to a placement
@socketio.on("messagePlacement")
def message_placement(data):
    
    # extract user object from session
    user_object = User.database[session["user_key"]]

    # retrieve placement title and company name 
    placement_title = data["placementTitle"]
    company_name = data["placementCompanyName"]
    # get placement from Placement.global_placements dictionary
    current_placement = Placement.global_placements[(company_name, placement_title)]

    company_object = Company.name_to_object[company_name]
    company_object.notifications_stack.push(["Added users to message group", "Application", datetime.today().strftime("%Y-%m-%d"), "Added student to '" + placement_title + "' message group."])

    # for all students who applied to the placement
    for student in current_placement.applied_students:
        # add students to company messaging list
        user_object.message_dictionary[student.email] = [Stack(), student]
        # add company to students messaging list  
        student.message_dictionary[user_object.email] = [Stack(), user_object] 
        # add notification to user
        student.notifications_stack.push(["Added to message group by '" + company_name + "'", "Application", datetime.today().strftime("%Y-%m-%d"), "Added to message group for placement '" + placement_title + "' by company '" + company_name + "'"])

    # forward the user to the messaging web page
    emit("forwardMessages")
    
# return an array of users and their email addresses, so that the HTML can reference these values when sending messages
@socketio.on("retrieveMessagers")
def retrieve_messagers():

    # extract user object from session
    user_object = User.database[session["user_key"]]
    message_data = [] # contains a list of json objects with username, email pairs
    # iterate through list of users messaged and store username, emails
    for other_email in user_object.message_dictionary:
        _, other_object = user_object.message_dictionary[other_email]
        other_json = {"email": other_email, "username": other_object.username}
    
    emit("retrievedMessagers", message_data)
    

# return the messages in a conversation given email address of other
@socketio.on("retrieveMessages")
def retrieve_messages(data):
    # extract user object from session
    user_object = User.database[session["user_key"]]
    # get email of other user
    other_email = data["email"]
    # return array of all messages
    message_stack, _ = user_object.message_dictionary[other_email]
    message_array = message_stack.array_copy()
    return emit("retrievedMessages", message_array)

# return the last online date of a given user
@socketio.on("retrieveMessagerDetails")
def retrieve_messager_details(data):
    # extract user object from session
    user_object = User.database[session["user_key"]]
    # get email of other user
    other_email = data["email"]
    _, other_object = user_object.message_dictionary[other_email]
    # return last online date of other user
    emit("retrievedMessagerDetails", {"username": other_object.username, "last_online": other_object.last_online})

# send a message to user given email
@socketio.on("sendMessage")
def send_message(data):
    # extract user object from session
    user_object = User.database[session["user_key"]]
    # get email of other user
    other_email = data["email"]
    # get msg sent
    msg_text = data["msg"]

    user_msg_stack, other_object = user_object.message_dictionary[other_email]
    other_msg_stack, _ = other_object.message_dictionary[user_object.email]
    # send message by adding to self.user stack and other users stack
    user_msg_stack.push([msg_text, 0])
    other_msg_stack.push([msg_text, 1])    

# navigate message page
@app.route("/messages/")
def message():
    # extract user object from session
    user_object = User.database[session["user_key"]]
    # update the user object last_online property
    user_object.last_online = datetime.today().strftime("%Y-%m-%d")
    return render_template("messages.html")

# return email, username and placements of given page
@socketio.on("retrieveCompanyPage")
def retrieve_company_page(data):
    # extract company using global company dictionary
    company_name = data["username"]
    company_object = Company.name_to_object[company_name]
    emit("retrievedCompanyPage", {"username": company_object.username, "email": company_object.email, 
    "placements": [company_object.placements[placement_title].json_summary() for placement_title in company_object.placements]})

# return if company is being followed by current user
@socketio.on("doesFollow")
def does_follow(data):
    # does current user exist? (anonymous user)
    if not "user_key" in session: return 
    # extract user object from session
    user_object = User.database[session["user_key"]]
    # get company object we are checking if is followed
    followed_name = data["username"]
    followed_user = Company.name_to_object[followed_name]
    # is object in follow set
    if followed_user in user_object.follow_set:
        return emit("followResult", {"doesFollow": True})
    # does not follow user
    else:
        return emit("followResult", {"doesFollow": False})

@socketio.on("toggleFollow")
def toggle_follow(data):
    # does current user exist? (anonymous user)
    if not "user_key" in session: return 
    # extract user object from session
    user_object = User.database[session["user_key"]]
    # get company object we are checking if is followed
    followed_name = data["username"]
    followed_user = Company.name_to_object[followed_name]
    # is object in follow set
    if followed_user in user_object.follow_set:
        user_object.follow_set.discard(followed_user)
        followed_user.followed_by.discard(user_object)
        # add notifications
        user_object.notifications_stack.push(["Unfollowed '" + followed_name + "'", "Unfollowed", datetime.today().strftime("%Y-%m-%d"), "You unfollowed the company '" + followed_name + "'"])
        followed_user.notifications_stack.push(["Unfollowed by '" + user_object.username + "'", "Unfollowed", datetime.today().strftime("%Y-%m-%d"), "You were unfollowed by '" + user_object.username + "'"])
        return emit("followResult", {"doesFollow": False})
    # does not follow user
    else:
        user_object.follow_set.add(followed_user)
        followed_user.followed_by.add(user_object)
        # add notifications
        user_object.notifications_stack.push(["Followed '" + followed_name + "'", "Followed", datetime.today().strftime("%Y-%m-%d"), "You followed the company '" + followed_name + "'"])
        followed_user.notifications_stack.push(["Followed by '" + user_object.username + "'", "Followed", datetime.today().strftime("%Y-%m-%d"), "You were followed by '" + user_object.username + "'"])
        return emit("followResult", {"doesFollow": True})

# navigate to company page
@app.route("/company/<company_name>")
def company_page(company_name):
    return render_template("company_page.html", username = company_name)

# return all notifications from notification stack
@socketio.on("notificationRequest")
def notification_request():
    # extract user object from session
    user_object = User.database[session["user_key"]]
    return emit("notificationResponse", {"notifications": user_object.notifications_stack.array_copy()})

# navigate to notifications page
@app.route("/notifications")
def notifications():
    return render_template("notifications.html")

# run application
socketio.run(app, host = "0.0.0.0", port = 8080, debug = True)

