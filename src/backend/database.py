"""
MongoDB database configuration and setup for Mergington High School API
"""

from argon2 import PasswordHasher

# Simple in-memory database for testing
class MockCollection:
    def __init__(self):
        self.data = {}
    
    def find(self, query=None):
        results = []
        for key, value in self.data.items():
            doc = {"_id": key, **value}
            
            # Apply filtering if query is provided
            if query:
                match = True
                
                # Check day filter
                if "schedule_details.days" in query:
                    day_filter = query["schedule_details.days"]
                    if "$in" in day_filter:
                        target_days = day_filter["$in"]
                        activity_days = doc.get("schedule_details", {}).get("days", [])
                        if not any(day in activity_days for day in target_days):
                            match = False
                
                # Check start time filter
                if "schedule_details.start_time" in query:
                    time_filter = query["schedule_details.start_time"]
                    if "$gte" in time_filter:
                        target_time = time_filter["$gte"]
                        activity_time = doc.get("schedule_details", {}).get("start_time", "")
                        if activity_time < target_time:
                            match = False
                
                # Check end time filter
                if "schedule_details.end_time" in query:
                    time_filter = query["schedule_details.end_time"]
                    if "$lte" in time_filter:
                        target_time = time_filter["$lte"]
                        activity_time = doc.get("schedule_details", {}).get("end_time", "")
                        if activity_time > target_time:
                            match = False
                
                if match:
                    results.append(doc)
            else:
                results.append(doc)
        
        return results
    
    def find_one(self, query):
        if isinstance(query, dict) and "_id" in query:
            return self.data.get(query["_id"])
        return None
    
    def insert_one(self, doc):
        if "_id" in doc:
            self.data[doc["_id"]] = doc
        return True
    
    def update_one(self, query, update):
        if isinstance(query, dict) and "_id" in query:
            doc_id = query["_id"]
            if doc_id in self.data:
                if "$push" in update:
                    for field, value in update["$push"].items():
                        if field not in self.data[doc_id]:
                            self.data[doc_id][field] = []
                        self.data[doc_id][field].append(value)
                if "$pull" in update:
                    for field, value in update["$pull"].items():
                        if field in self.data[doc_id]:
                            try:
                                self.data[doc_id][field].remove(value)
                            except ValueError:
                                pass
                return type('MockResult', (), {'modified_count': 1})()
        return type('MockResult', (), {'modified_count': 0})()
    
    def count_documents(self, query):
        return len(self.data)
    
    def aggregate(self, pipeline):
        # Simple implementation for getting unique days
        days = set()
        for activity in self.data.values():
            if "schedule_details" in activity and "days" in activity["schedule_details"]:
                days.update(activity["schedule_details"]["days"])
        return [{"_id": day} for day in sorted(days)]

# Use mock collections
activities_collection = MockCollection()
teachers_collection = MockCollection()

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    },
    "Manga Maniacs": {
        "description": "Mergulhe no universo épico dos mangás japoneses! Descubra mundos de ninjas, magos, heróis e aventuras incríveis. Discuta suas séries favoritas, desenhe seus próprios personagens e faça parte de uma comunidade apaixonada pela arte japonesa que conquistou o mundo!",
        "schedule": "Tuesdays, 7:00 PM - 8:00 PM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "19:00",
            "end_time": "20:00"
        },
        "max_participants": 15,
        "participants": []
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]

