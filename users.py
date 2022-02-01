import hashlib, uuid
from placement import *

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
        return True, new_user_object, (email, salted_password, salt_string)

    @staticmethod
    def login(email, password):
        """ return relevant user object if user exists """
        for user_database_key in User.database:
            (key_email, salted_password, salt_string) = user_database_key
            if key_email != email: continue
            if salted_password == User.salt_password(password, salt_string)[0]:
                # correct login -> true, user object
                return True, User.database[(email, salted_password, salt_string)], (email, salted_password, salt_string)
            else:
                # incorrect login -> false, none
                return False, None, (email, salted_password, salt_string)

class Student(User):
    def __init__(self, email, username):
        User.__init__(self, email, username)

class Company(User):
    def __init__(self, email, username):
        User.__init__(self, email, username)
        self.placements = {} # title -> placement object

    """ create and return Bool, new placement object """
    def create_new_placement(self, title, description, date_range, location_tag, subject_tags):
        # check for existing placement with the same name
        if title in self.placements:
            return False, None
        else:
            new_placement = Placement(title, description, self, date_range, location_tag, subject_tags)
            self.placements[new_placement.title] = new_placement
            return True, new_placement

    """ edit placement given placement title and new values, return placement object """
    def edit_placement(self, title, description = None, date_range = None, location_tag = None, subject_tags = None):
        if not (title in self.placements): return None 
        placement_object = self.placements[title]
        if title: placement_object.title = title
        if description: placement_object.description = description
        if date_range: placement_object.date_range = date_range
        if location_tag: placement_object.location_tag = location_tag
        if subject_tags: placement_object.subject_tags = subject_tags
        return placement_object

    """ delete placement given placement title"""
    def delete_placement(self, title):
        if not (title in self.placements): return None
        del self.placements[title]
        
if __name__ == "__main__":
    _, new_company = User.register("name@email.com", "username", "password123!", False)
    new_placement = new_company.create_new_placement("Title", "Description", DateRange(Date(1,1,1), Date(2,2,2)), LocationTag("Berkshire"), [])
    new_company.edit_placement("Title", "New Description")
    print(new_company.placements["Title"].description) # outputs "New Description"

