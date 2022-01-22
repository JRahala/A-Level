import hashlib, uuid

class User(object):
    """
    Stores all the information and shared actions between Student and Company objects
    """
    database = {}
    emails = set()
    def __init__(self, email, username):
        self.email = email
        self.username = username

    @staticmethod
    def salt_password(password, salt = None):
        """ returns salted password + random salt """
        if salt == None: salt = uuid.uuid4().hex
        return hashlib.sha512((password + salt).encode()).hexdigest(), salt

    @classmethod
    def register(cls, email, username, password, is_student):
        """ creates user and stores into User.database dictionary """
        if email in User.emails: return False, None
        salted_password, salt_string = User.salt_password(password)
        if is_student: new_user_object = Student(email, username)
        else: new_user_object = Company(email, username)
        User.database[(email, salted_password, salt_string)] = new_user_object
        return True, new_user_object

    @staticmethod
    def login(email, password):
        """ return relevant user object if user exists """
        for user_database_key in User.database:
            (key_email, salted_password, salt_string) = user_database_key
            if key_email != email: continue
            if salted_password == User.salt_password(password, salt_string)[0]:
                # correct login -> true, user object
                return True, User.database[(email, salted_password, salt_string)]
            else:
                # incorrect login -> false, none
                return False, None

class Student(User):
    def __init__(self, email, username):
        User.__init__(email, username)

class Company(User):
    def __init__(self, email, username):
        User.__init__(email, username)


if __name__ == "__main__":
    new_user = User.register("name@email.com", "username1", "password")
    new_user = User.register("name@email.com", "username2", "password")
    requested_user = User.login("name@email.com", "password")
    print(requested_user.username) # outputs username1

