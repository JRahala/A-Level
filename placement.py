""" describes a specific area or subject area related to work experience placement """
from datetime import date


class SubjectTag:
    all_subject_tags = set() # stores all subjects tag strings ever

    def __init__(self, subject):
        self.subject = subject
    
    """ used for autocomplete request from client.html """
    @classmethod
    def get_all_subject_tags(cls):
        return list(cls.all_subject_tags)

    """ create new subject tag and add to set """
    @classmethod
    def create_new_subject_tag(cls, subject):
        cls.all_subject_tags.add(subject)


""" the county of a work experience """
class LocationTag:
    all_location_tags = ["Berkshire", "Oxfordshire", "Cambridgeshire"] # for now I have put three counties in, fill in with csv later
    def __init__(self, location):
        self.location = location

    """ user for autocomplete request from client.html """
    @classmethod
    def get_all_location_tags(cls):
        return cls.all_location_tags
    

""" date tag, stores day, month, year """
class Date:
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year


""" date range stores an interval of dates from start_date to end_date, caches duration for display purposes """
class DateRange:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.duration = 0


""" stores work experience placements with DateRange, [SubjectTag] and Location tag """
class Placement:
    def __init__(self, title, description, company, date_range, location_tag, subject_tags):
        self.title = title
        self.description = description
        self.company = company
        self.date_range = date_range
        self.location_tag = location_tag
        self.subject_tags = subject_tags
    
