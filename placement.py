""" describes a specific area or subject area related to work experience placement """
from datetime import date


class SubjectTag:
    all_subject_tags = set() # stores all subjects tag strings ever

    def __init__(self, subject):
        self.subject = subject
        SubjectTag.create_new_subject_tag(self)
    
    """ used for autocomplete request from client.html """
    @classmethod
    def get_all_subject_tags(cls):
        return list(cls.all_subject_tags)

    """ create new subject tag and add to set """
    @classmethod
    def create_new_subject_tag(cls, subject):
        cls.all_subject_tags.add(subject)
    
    # return a hashable dictionary summary of date
    def json_summary(self):
        return self.subject


""" the county of a work experience """
class LocationTag:
    all_location_tags = ["Berkshire", "Oxfordshire", "Cambridgeshire"] # for now I have put three counties in, fill in with csv later
    def __init__(self, location):
        self.location = location

    """ user for autocomplete request from client.html """
    @classmethod
    def get_all_location_tags(cls):
        return cls.all_location_tags

    # return a hashable dictionary summary of location tag
    def json_summary(self):
        return self.location
    

""" date tag, stores day, month, year """
class Date:
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

    # return a hashable dictionary summary of date
    def json_summary(self):
        if self.year <= 9:
            text_year = "200" + str(self.year)
        else:
            text_year = "20" + str(self.year)

        if self.month <= 9:
            text_month = "0" + str(self.month)
        
        if self.day <= 9:
            text_day = "0" + str(self.day)
        
        return f"{text_year}-{text_month}-{text_day}"

""" date range stores an interval of dates from start_date to end_date, caches duration for display purposes """
class DateRange:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.duration = 0

    # return a hashable dictionary summary of date_range
    def json_summary(self):
        return {
            "start_date": self.start_date.json_summary(),
            "end_date": self.end_date.json_summary()
        }


""" stores work experience placements with DateRange, [SubjectTag] and Location tag """
class Placement:
    def __init__(self, title, description, company, date_range, location_tag, subject_tags):
        self.title = title
        self.description = description
        self.company = company
        self.date_range = date_range
        self.location_tag = location_tag
        self.subject_tags = subject_tags

    # return a hashable dictionary summary of the placement
    def json_summary(self):
        return {
            "title": self.title,
            "description": self.description,
            "company": self.company.username,
            "date_range_tag": self.date_range.json_summary(),
            "location_tag": self.location_tag.json_summary(),
            "subject_tags": [subject_tag.json_summary() for subject_tag in self.subject_tags]
        }
    
