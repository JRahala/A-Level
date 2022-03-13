""" describes a specific area or subject area related to work experience placement """
from datetime import date
import math
import pickle
from data_structures import *

""" Subject Tag class: subject area of work experience """
class SubjectTag:
    all_subject_tags = set() # stores all subjects tag strings

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


""" Location Tag class: the county of a work experience """
class LocationTag:
    distance_dictionary = {}
    def __init__(self, location):
        self.location = location

    """ user for autocomplete request from client.html """
    @classmethod
    def get_all_location_tags(cls):
        return tuple(cls.distance_dictionary.keys())

    # return a hashable dictionary summary of location tag
    def json_summary(self):
        return self.location

    # return the distance (in metres) between two points of longitude and latitude 
    @staticmethod
    def distance(latitude1, longitude1, latitude2, longitude2):
        radius = 6371e3 # calculation in metres
        phi1 = latitude1 * math.pi / 180 # convert to radians
        phi2 = latitude2 * math.pi / 180 # convert to radians
        
        d_phi = (latitude2 - latitude1) * math.pi / 180
        d_lambda = (longitude2 - longitude1) * math.pi / 180

        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return radius * c

    # return all location tags within x km from given location tag
    @staticmethod
    def get_locations_within(city_name, range_m):

        left_index = 0
        right_index = len(LocationTag.distance_dictionary[city_name])

        while left_index < right_index:
            # print(left_index, right_index)
            middle_index = (left_index + right_index) // 2
            if LocationTag.distance_dictionary[city_name][middle_index][1] <= range_m:
                left_index = middle_index + 1
            else:
                right_index = middle_index

        return [LocationTag(city_name) for city_name in LocationTag.distance_dictionary[city_name][:middle_index]]
    
# load distance_dictionary.pickle as LocationTag.distance_dictionary
file = open("distance_dictionary.pickle",'rb')
LocationTag.distance_dictionary = pickle.load(file)
file.close()

""" Date Tag class: stores day, month, year """
class Date:
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

    # return number of days since 01/01/2000 with (1,1,0) = 0
    def duration(self):

        # durations[n] = days from start of year up to start of month[n] where month[0] = january
        MONTH_DURATIONS = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]

        # number of days in whole years
        count = self.year * 365
        # add days from self.day
        count += self.day

        # add number of days in each whole month (not include current month)
        count += MONTH_DURATIONS[self.month - 1]

        # account for leap years
        starting_year = self.year
        leap_years = 0

        # if before febuary, do not account for the current year
        if (self.month <= 2): starting_year -= 1

        leap_years += starting_year / 4
        leap_years -= starting_year / 100
        leap_years += starting_year / 400
        return count + leap_years

    # return a hashable dictionary summary of date
    def json_summary(self):
        if self.year <= 9:
            text_year = "200" + str(self.year)
        else:
            text_year = "20" + str(self.year)

        if self.month <= 9:
            text_month = "0" + str(self.month)
        else:
            text_month = str(self.month)
        
        if self.day <= 9:
            text_day = "0" + str(self.day)
        else:
            text_day = str(self.day)

        return f"{text_year}-{text_month}-{text_day}"

""" Date Range class: stores an interval of dates from start_date to end_date, caches duration for display purposes """
class DateRange:
    def __init__(self, start_date, end_date):
        # switch dates if the start date comes after the end date
        if start_date.duration() > end_date.duration():
            start_date, end_date = end_date, start_date

        self.start_date = start_date
        self.end_date = end_date

    # return a hashable dictionary summary of date_range
    def json_summary(self):
        return {
            "start_date": self.start_date.json_summary(),
            "end_date": self.end_date.json_summary()
        }

    # return the number of dates between the start and end dates 
    def duration(self):
        return self.end_date.duration() - self.start_date.duration()

    # return the date range of overlap between two date ranges: range_a, range, b
    @staticmethod 
    def overlap(range_a, range_b):
        # set range_a as the range with the earliest start_date
        if (range_a.start_date.duration() > range_b.start_date.duration()):
            range_a, range_b = range_b, range_a

        # check for no-overlap
        if (range_a.end_date.duration() < range_b.start_date.duration()):
            return DateRange(Date(1,1,0), Date(1,1,0))

        # check for full-overlap
        if (range_a.end_date.duration() > range_b.end_date.duration()):
            return DateRange(range_b.start_date, range_b.end_date)

        # partial overlap
        return DateRange(range_b.start_date, range_a.end_date) 

""" stores work experience placements with DateRange, [SubjectTag] and Location tag """
class Placement:
    
    # Create global placement dictionary for all users to access read only placement json_summaries
    # reference using(company_name, placement_title)
    global_placements = {}

    def __init__(self, title, description, company, date_range, location_tag, subject_tags):
        self.title = title
        self.description = description
        self.company = company
        self.date_range = date_range
        self.location_tag = location_tag
        self.subject_tags = subject_tags
        self.applied_students = set()

    # return a read only json_summary of placement 
    @staticmethod
    def lookup_placement(company_name, placement_title):
        if (company_name, placement_title) in Placement.global_placements:
            return Placement.global_placements[(company_name, placement_title)]
        return None

    # remove a placement from the subject trie and global_placements dict
    @staticmethod
    def delete_placement(company_name, placement_title):
        if (company_name, placement_title) in Placement.global_placements:
            # get reference to current_placement
            current_placement = Placement.global_placements[(company_name, placement_title)]
            # remove from subject trie
            Placement.subject_trie.delete(current_placement, [subject_tag.subject for subject_tag in current_placement.subject_tags])
            # remove from global_placements 
            del Placement.global_placements[(company_name, placement_title)]
        # placement does not exist
        return None
    
    # insert placement into the subject_trie and global_placements dict
    @staticmethod
    def insert_subject_trie(company_name, placement_title, placement):
        # add to global_placements dict
        Placement.global_placements[(company_name, placement_title)] = placement
        # insert into subject_trie
        Placement.subject_trie.insert(placement, filters = [subject_tag.subject for subject_tag in placement.subject_tags])
        return None

    # search for a placement using the subject_trie via subject_tags: [SubjectTag()]
    @staticmethod
    def search_subject_trie(subject_tags):
        return Placement.subject_trie.search(filters = [subject_tag.subject for subject_tag in subject_tags])

    # dirtysearch for a placement using the subject_trie via subject_tags: [SubjectTag()]
    @staticmethod
    def dirty_search_subject_trie(subject_tags):
        return Placement.subject_trie.dirty_search(filters = [subject_tag.subject for subject_tag in subject_tags])

    # filter placements by date range and locations
    @staticmethod
    def filter_placements(placements_list, ideal_date_range, ideal_location, location_range):

        # get locations that are within range, take first element is place, second element is distance
        allowed_locations = [location_tag.location[0] for location_tag in LocationTag.get_locations_within(ideal_location.location, location_range)]

        # iterate through placements_list
        index = 0
        while index < len(placements_list):
            current_placement = placements_list[index]
            
            # remove all placements that do not overlap with ideal_date_range
            if DateRange.overlap(ideal_date_range, current_placement.date_range).duration() <= 0:
                placements_list.pop(index)
                
            # remove all placements that are too far away from location_range
            if not (current_placement.location_tag.location in allowed_locations):
                placements_list.pop(index)
                
            else:
                index += 1

        # return remaining placements
        return placements_list


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

# Create subject trie inside placement class
Placement.subject_trie = Trie()

if __name__ == "__main__":
    pass