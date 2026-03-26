"""
Sample Data Generator for Ride-Sharing Analytics Pipeline
Generates realistic ride-sharing data (rides, drivers, passengers)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import string
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_DRIVERS = 2000
NUM_PASSENGERS = 5000
NUM_RIDES = 50000
# Generate data for current date
CURRENT_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
START_DATE = CURRENT_DATE
END_DATE = CURRENT_DATE
OUTPUT_DIR = Path("data/raw")

# San Francisco Bay Area neighborhoods with coordinates
NEIGHBORHOODS = {
    "Downtown SF": (37.7749, -122.4194),
    "Mission District": (37.7599, -122.4148),
    "SOMA": (37.7749, -122.4094),
    "Marina": (37.8024, -122.4358),
    "Pacific Heights": (37.7925, -122.4381),
    "Castro": (37.7618, -122.4350),
    "Haight-Ashbury": (37.7699, -122.4469),
    "North Beach": (37.8067, -122.4100),
    "Chinatown": (37.7941, -122.4078),
    "Financial District": (37.7946, -122.3998),
    "Oakland": (37.8044, -122.2711),
    "Berkeley": (37.8715, -122.2730),
    "San Jose": (37.3382, -121.8863),
    "Palo Alto": (37.4419, -122.1430),
    "Mountain View": (37.3861, -122.0839),
}

# Vehicle types with realistic distribution
VEHICLE_TYPES = {
    "Sedan": 0.40,
    "SUV": 0.25,
    "Economy": 0.20,
    "Luxury": 0.10,
    "Van": 0.05
}

# Payment methods with realistic distribution
PAYMENT_METHODS = {
    "Credit Card": 0.45,
    "Debit Card": 0.20,
    "Apple Pay": 0.15,
    "PayPal": 0.12,
    "Cash": 0.08
}

# First and last names for realistic name generation
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Frank", "Christine", "Gregory", "Debra",
    "Raymond", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Virginia",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Julie",
    "Jose", "Joyce", "Henry", "Victoria", "Adam", "Kelly", "Douglas", "Christina",
    "Nathan", "Joan", "Zachary", "Evelyn", "Kyle", "Judith", "Noah", "Megan",
    "Ethan", "Cheryl", "Jeremy", "Andrea", "Walter", "Hannah", "Christian", "Jacqueline",
    "Keith", "Martha", "Roger", "Gloria", "Terry", "Teresa", "Gerald", "Sara",
    "Harold", "Janice", "Sean", "Marie", "Austin", "Julia", "Carl", "Grace",
    "Arthur", "Judy", "Lawrence", "Theresa", "Dylan", "Madison", "Jesse", "Beverly",
    "Jordan", "Denise", "Bryan", "Marilyn", "Billy", "Amber", "Joe", "Danielle",
    "Bruce", "Rose", "Gabriel", "Brittany", "Logan", "Diana", "Albert", "Abigail",
    "Willie", "Jane", "Alan", "Lori", "Juan", "Kathryn", "Wayne", "Alexis",
    "Roy", "Marie", "Ralph", "Olivia", "Randy", "Tiffany", "Eugene", "Kimberly",
    "Vincent", "Emily", "Russell", "Deborah", "Louis", "Amy", "Philip", "Angela",
    "Bobby", "Ashley", "Johnny", "Emma", "Howard", "Cynthia", "Ethan", "Marie"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
    "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez",
    "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
    "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards",
    "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers",
    "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey", "Reed", "Kelly",
    "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks",
    "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross",
    "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell",
    "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher", "Vasquez", "Simmons",
    "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham", "Reynolds", "Griffin",
    "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant", "Herrera", "Gibson",
    "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray", "Ford", "Castro",
    "Marshall", "Owens", "Harrison", "Fernandez", "Mcdonald", "Woods", "Washington", "Kennedy",
    "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb", "Tucker", "Guzman",
    "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter", "Gordon", "Mendez",
    "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Munoz", "Hunt", "Hicks",
    "Holmes", "Palmer", "Wagner", "Black", "Robertson", "Boyd", "Rose", "Stone",
    "Salazar", "Fox", "Warren", "Mills", "Meyer", "Rice", "Schmidt", "Garza",
    "Daniels", "Ferguson", "Nichols", "Stephens", "Soto", "Weaver", "Ryan", "Gardner",
    "Payne", "Grant", "Dunn", "Kelley", "Spencer", "Hawkins", "Arnold", "Pierce",
    "Vazquez", "Hansen", "Peters", "Santos", "Hart", "Bradley", "Knight", "Elliott",
    "Cunningham", "Duncan", "Armstrong", "Hudson", "Carroll", "Lane", "Riley", "Andrews",
    "Alvarado", "Ray", "Delgado", "Berry", "Perkins", "Hoffman", "Johnston", "Matthews",
    "Pena", "Richards", "Contreras", "Willis", "Carpenter", "Lawrence", "Sandoval", "Guerrero",
    "George", "Chapman", "Rios", "Estrada", "Ortega", "Watkins", "Greene", "Nunez",
    "Wheeler", "Valdez", "Harper", "Lynch", "Barker", "Obrien", "Mccoy", "Curtis",
    "Briggs", "Newton", "Reid", "Parks", "Casey", "Baldwin", "Hammond", "Flowers",
    "Cobb", "Moody", "Quinn", "Blake", "Maxwell", "Pope", "Floyd", "Osborne",
    "Paul", "Mccarthy", "Guerrero", "Lindsey", "Estrada", "Sandoval", "Gibbs", "Tyler",
    "Gross", "Fitzgerald", "Stokes", "Doyle", "Sherman", "Saunders", "Wise", "Colon",
    "Gill", "Alvarado", "Greer", "Padilla", "Simon", "Waters", "Nunez", "Ballard",
    "Schwartz", "Mcbride", "Houston", "Christensen", "Klein", "Pratt", "Briggs", "Parsons",
    "Mclaughlin", "Zimmerman", "French", "Buchanan", "Moran", "Copeland", "Roy", "Pittman",
    "Brady", "Mccormick", "Holloway", "Brock", "Poole", "Frank", "Logan", "Owen",
    "Bass", "Marsh", "Drake", "Wong", "Jefferson", "Park", "Morton", "Abbott",
    "Sparks", "Patrick", "Norton", "Huff", "Clayton", "Massey", "Lloyd", "Figueroa",
    "Carson", "Bowers", "Roberson", "Barton", "Tran", "Lamb", "Harrington", "Casey",
    "Boone", "Cortez", "Clarke", "Mathis", "Singleton", "Wilkins", "Cain", "Bryan",
    "Underwood", "Hogan", "Mckenzie", "Collier", "Luna", "Phelps", "Mcguire", "Allison",
    "Bridges", "Wilkerson", "Nash", "Summers", "Atkins", "Wilcox", "Pitts", "Conley",
    "Marquez", "Burnett", "Richard", "Cochran", "Chase", "Davenport", "Hood", "Gates",
    "Clay", "Ayala", "Sawyer", "Roman", "Vazquez", "Dickerson", "Hodge", "Acosta",
    "Flynn", "Espinoza", "Nicholson", "Monroe", "Wolf", "Morrow", "Kirk", "Randall",
    "Anthony", "Whitaker", "Oconnor", "Skinner", "Ware", "Molina", "Kirby", "Huffman",
    "Bradford", "Charles", "Gilmore", "Dominguez", "Oneal", "Bruce", "Lang", "Combs",
    "Kramer", "Heath", "Hancock", "Gallagher", "Gaines", "Shaffer", "Short", "Wiggins",
    "Mathews", "Mcclain", "Fischer", "Wall", "Small", "Melton", "Hensley", "Bond",
    "Dyer", "Cameron", "Grimes", "Contreras", "Christian", "Wyatt", "Baxter", "Snow",
    "Mosley", "Shepherd", "Larsen", "Hoover", "Beasley", "Glenn", "Petersen", "Whitehead",
    "Meyers", "Keith", "Garrison", "Vincent", "Shields", "Horn", "Savage", "Olsen",
    "Schroeder", "Hartman", "Woodard", "Mueller", "Kemp", "Deleon", "Booth", "Patel",
    "Calhoun", "Wiley", "Eaton", "Cline", "Navarro", "Harrell", "Lester", "Humphrey",
    "Parrish", "Duran", "Hutchinson", "Hess", "Dorsey", "Bullock", "Robles", "Beard",
    "Dalton", "Avila", "Vance", "Rich", "Blackwell", "York", "Johns", "Blankenship",
    "Trevino", "Salinas", "Campos", "Pruitt", "Moses", "Callahan", "Golden", "Montoya",
    "Hardin", "Guerra", "Mcdowell", "Carey", "Stafford", "Gallegos", "Henson", "Wilkinson",
    "Booker", "Merritt", "Miranda", "Atkinson", "Orr", "Decker", "Hobbs", "Preston",
    "Tanner", "Knox", "Pacheco", "Stephenson", "Glass", "Rojas", "Serrano", "Marks",
    "Hickman", "English", "Sweeney", "Strong", "Prince", "Mcclure", "Conway", "Walter",
    "Roth", "Maynard", "Farrell", "Lowery", "Hurst", "Nixon", "Weiss", "Trujillo",
    "Ellison", "Sloan", "Juarez", "Winters", "Mclean", "Randolph", "Leon", "Boyer",
    "Villarreal", "Mccall", "Gentry", "Carrillo", "Kent", "Ayers", "Lara", "Shannon",
    "Sexton", "Pace", "Hull", "Leblanc", "Browning", "Velasquez", "Leach", "Chang",
    "House", "Sellers", "Herring", "Noble", "Foley", "Bartlett", "Mercado", "Landry",
    "Durham", "Walls", "Barr", "Mckee", "Bauer", "Rivers", "Everett", "Bradshaw",
    "Pugh", "Velez", "Rush", "Estes", "Dodson", "Morse", "Sheppard", "Weeks",
    "Camacho", "Bean", "Barron", "Livingston", "Middleton", "Spears", "Branch", "Blevins",
    "Chen", "Kerr", "Mcconnell", "Hatfield", "Harding", "Ashley", "Solis", "Herman",
    "Frost", "Giles", "Blackburn", "William", "Pennington", "Woodward", "Finley", "Mcintosh",
    "Koch", "Best", "Solomon", "Mccullough", "Dudley", "Nolan", "Blanchard", "Rivas",
    "Brennan", "Mejia", "Kane", "Benton", "Joyce", "Buckley", "Haley", "Valentine",
    "Maddox", "Russo", "Mcknight", "Buck", "Moon", "Mcmillan", "Crosby", "Berg",
    "Dotson", "Mays", "Roach", "Church", "Chan", "Richmond", "Meadows", "Faulkner",
    "Oneill", "Knapp", "Kline", "Barry", "Ochoa", "Jacobson", "Gay", "Avery",
    "Hendricks", "Horne", "Shepard", "Hebert", "Cherry", "Cardenas", "Mcintyre", "Whitney",
    "Waller", "Holman", "Donaldson", "Cantu", "Terrell", "Morin", "Gillespie", "Fuentes",
    "Tillman", "Sanford", "Bentley", "Peck", "Key", "Salas", "Rollins", "Gamble",
    "Dickson", "Odom", "Acevedo", "Morrison", "Strickland", "Nash", "Lindsey", "Yates",
    "Lynn", "Buchanan", "Bond", "Morton", "Melendez", "Oconnor", "Hendrix", "Rasmussen",
    "Tanner", "Lamb", "Holloway", "Valdez", "Cline", "Osborn", "Delacruz", "Collier",
    "Pittman", "Velazquez", "Barrera", "Huynh", "Barrera", "Huynh", "Barrera", "Huynh"
]


def generate_realistic_name():
    """Generate a realistic full name"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return f"{first_name} {last_name}"


def generate_realistic_email(name):
    """Generate realistic email from name"""
    name_parts = name.lower().split()
    first = name_parts[0]
    last = name_parts[1] if len(name_parts) > 1 else ""
    
    # Various email patterns
    patterns = [
        f"{first}.{last}",
        f"{first}{last}",
        f"{first}{random.randint(10, 99)}",
        f"{first[0]}{last}",
        f"{first}.{last[0]}",
    ]
    
    email_local = random.choice(patterns)
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com"]
    return f"{email_local}@{random.choice(domains)}"


def generate_realistic_phone():
    """Generate realistic US phone number"""
    area_codes = ["415", "510", "650", "408", "925", "707", "831", "209"]
    area_code = random.choice(area_codes)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    return f"+1-{area_code}-{exchange}-{number}"


def generate_ca_license_plate():
    """Generate realistic California license plate"""
    # CA format: 1ABC234 or ABC1234
    if random.random() < 0.5:
        # Format: 1ABC234
        num = random.randint(1, 9)
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        digits = random.randint(100, 999)
        return f"{num}{letters}{digits}"
    else:
        # Format: ABC1234
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        digits = random.randint(1000, 9999)
        return f"{letters}{digits}"


def weighted_choice(choices_dict):
    """Choose from dictionary with weights"""
    items = list(choices_dict.keys())
    weights = list(choices_dict.values())
    return np.random.choice(items, p=weights)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    R = 6371  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat/2)**2 + 
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c


def generate_drivers(num_drivers):
    """Generate realistic driver data"""
    drivers = []
    cities = list(NEIGHBORHOODS.keys())
    
    for i in range(1, num_drivers + 1):
        name = generate_realistic_name()
        email = generate_realistic_email(name)
        phone = generate_realistic_phone()
        
        # Registration date - some drivers are newer, some older
        days_ago = int(np.random.exponential(180))  # Exponential distribution
        days_ago = min(days_ago, 1095)  # Max 3 years
        registration_date = CURRENT_DATE - timedelta(days=days_ago)
        
        # Vehicle type with realistic distribution
        vehicle_type = weighted_choice(VEHICLE_TYPES)
        
        # License plate
        license_plate = generate_ca_license_plate()
        
        # City/neighborhood
        city = random.choice(cities)
        
        # Rating - most drivers have good ratings, some have lower
        # Use beta distribution to get realistic rating distribution
        rating_raw = np.random.beta(8, 2)  # Skewed towards higher ratings
        rating = round(1 + rating_raw * 4, 2)  # Scale to 1-5
        rating = max(1.0, min(5.0, rating))  # Clamp to 1-5
        
        # Active status - drivers with lower ratings more likely to be inactive
        is_active_prob = 0.5 + (rating - 1) * 0.1  # 50% at rating 1, 90% at rating 5
        is_active = random.random() < is_active_prob
        
        drivers.append({
            "driver_id": f"DRV{i:06d}",
            "name": name,
            "email": email,
            "phone": phone,
            "registration_date": registration_date.strftime("%Y-%m-%d"),
            "vehicle_type": vehicle_type,
            "license_plate": license_plate,
            "city": city,
            "rating": rating,
            "is_active": is_active
        })
    
    return pd.DataFrame(drivers)


def generate_passengers(num_passengers):
    """Generate realistic passenger data"""
    passengers = []
    cities = list(NEIGHBORHOODS.keys())
    
    for i in range(1, num_passengers + 1):
        name = generate_realistic_name()
        email = generate_realistic_email(name)
        phone = generate_realistic_phone()
        
        # Registration date - exponential distribution (more recent registrations)
        days_ago = int(np.random.exponential(120))
        days_ago = min(days_ago, 730)  # Max 2 years
        registration_date = CURRENT_DATE - timedelta(days=days_ago)
        
        # City
        city = random.choice(cities)
        
        # Payment method with realistic distribution
        payment_method = weighted_choice(PAYMENT_METHODS)
        
        # Rating - passengers generally have higher ratings
        rating_raw = np.random.beta(9, 1.5)
        rating = round(1 + rating_raw * 4, 2)
        rating = max(1.0, min(5.0, rating))
        
        passengers.append({
            "passenger_id": f"PAS{i:06d}",
            "name": name,
            "email": email,
            "phone": phone,
            "registration_date": registration_date.strftime("%Y-%m-%d"),
            "city": city,
            "preferred_payment_method": payment_method,
            "rating": rating
        })
    
    return pd.DataFrame(passengers)


def generate_rides(num_rides, drivers_df, passengers_df):
    """Generate realistic ride data"""
    rides = []
    active_drivers = drivers_df[drivers_df["is_active"] == True]
    driver_ids = active_drivers["driver_id"].tolist()
    passenger_ids = passengers_df["passenger_id"].tolist()
    
    # Create ride frequency weights for passengers (some ride more often)
    passenger_weights = np.random.exponential(1.0, len(passenger_ids))
    passenger_weights = passenger_weights / passenger_weights.sum()
    
    # Create ride frequency weights for drivers (some drive more)
    driver_weights = np.random.exponential(1.0, len(driver_ids))
    driver_weights = driver_weights / driver_weights.sum()
    
    rides_per_day = num_rides // ((END_DATE - START_DATE).days + 1)
    
    # Probability distribution for hours (peak hours have more rides)
    # Hours: 0-6 (very low), 7-9 (peak AM), 10-14 (medium), 15-16 (medium-high), 17-19 (peak PM), 20-23 (low)
    hour_probs = np.array([
        0.005, 0.005, 0.005, 0.005, 0.01, 0.015, 0.02,  # 0-6 AM
        0.06, 0.07, 0.05,  # 7-9 AM (peak)
        0.03, 0.03, 0.03, 0.03, 0.03,  # 10-14 (lunch/afternoon)
        0.04, 0.05,  # 15-16
        0.08, 0.09, 0.07,  # 17-19 (peak PM)
        0.04, 0.03, 0.02, 0.01  # 20-23
    ])
    hour_probs = hour_probs / hour_probs.sum()
    
    for day in range((END_DATE - START_DATE).days + 1):
        date = START_DATE + timedelta(days=day)
        is_weekend = date.weekday() >= 5  # Saturday or Sunday
        
        # Adjust probabilities for weekends (more rides during day, less during commute)
        if is_weekend:
            hour_probs_weekend = np.array([
                0.01, 0.01, 0.01, 0.01, 0.015, 0.02, 0.025,  # 0-6 AM
                0.04, 0.05, 0.06,  # 7-9 AM
                0.05, 0.06, 0.07, 0.07, 0.06,  # 10-14 (more activity)
                0.06, 0.07,  # 15-16
                0.08, 0.09, 0.08,  # 17-19
                0.06, 0.05, 0.04, 0.03  # 20-23 (more night activity)
            ])
            hour_probs_weekend = hour_probs_weekend / hour_probs_weekend.sum()
            current_hour_probs = hour_probs_weekend
        else:
            current_hour_probs = hour_probs
        
        # Generate rides for this day
        for i in range(rides_per_day):
            # Pickup time
            hour = np.random.choice(list(range(24)), p=current_hour_probs)
            minute = random.randint(0, 59)
            pickup_datetime = date.replace(hour=hour, minute=minute)
            
            # Select driver and passenger based on frequency weights
            driver_id = np.random.choice(driver_ids, p=driver_weights)
            passenger_id = np.random.choice(passenger_ids, p=passenger_weights)
            
            # Pickup location - choose a neighborhood
            pickup_neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
            pickup_base_lat, pickup_base_lon = NEIGHBORHOODS[pickup_neighborhood]
            
            # Add some randomness within neighborhood (~2km radius)
            pickup_lat = pickup_base_lat + np.random.uniform(-0.018, 0.018)
            pickup_lon = pickup_base_lon + np.random.uniform(-0.018, 0.018)
            
            # Dropoff location - usually different neighborhood, sometimes same
            if random.random() < 0.3:  # 30% chance same neighborhood
                dropoff_neighborhood = pickup_neighborhood
            else:
                dropoff_neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
            
            dropoff_base_lat, dropoff_base_lon = NEIGHBORHOODS[dropoff_neighborhood]
            dropoff_lat = dropoff_base_lat + np.random.uniform(-0.018, 0.018)
            dropoff_lon = dropoff_base_lon + np.random.uniform(-0.018, 0.018)
            
            # Calculate distance
            distance_km = haversine_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
            
            # Ensure minimum distance (at least 0.5 km)
            if distance_km < 0.5:
                # Move dropoff further
                angle = np.random.uniform(0, 2 * np.pi)
                distance_km = np.random.uniform(0.5, 3.0)
                dropoff_lat = pickup_lat + (distance_km / 111) * np.cos(angle)
                dropoff_lon = pickup_lon + (distance_km / 111) * np.sin(angle) / np.cos(np.radians(pickup_lat))
            
            # Duration based on distance and traffic
            # Average speed: 30-50 km/h in city, slower during peak hours
            if hour in [7, 8, 17, 18, 19]:
                avg_speed = np.random.uniform(20, 35)  # Slower during peak
            else:
                avg_speed = np.random.uniform(35, 50)
            
            duration_minutes = max(5, int((distance_km / avg_speed) * 60))
            duration_minutes += np.random.randint(-3, 8)  # Add some variance
            duration_minutes = max(5, min(120, duration_minutes))  # Clamp 5-120 min
            
            dropoff_datetime = pickup_datetime + timedelta(minutes=duration_minutes)
            
            # Base fare calculation (realistic pricing)
            base_fare = 2.50
            per_km_rate = 1.75
            per_minute_rate = 0.30
            minimum_fare = 5.00
            
            fare_amount = base_fare + (distance_km * per_km_rate) + (duration_minutes * per_minute_rate)
            fare_amount = max(minimum_fare, fare_amount)
            
            # Surge pricing - more likely during peak hours and high demand
            is_peak = hour in [7, 8, 17, 18, 19]
            surge_multiplier = 1.0
            
            if is_peak:
                # Higher chance of surge during peak
                if random.random() < 0.35:  # 35% chance
                    surge_multiplier = round(np.random.uniform(1.2, 2.8), 2)
                    fare_amount *= surge_multiplier
            else:
                # Lower chance outside peak
                if random.random() < 0.05:  # 5% chance
                    surge_multiplier = round(np.random.uniform(1.1, 1.5), 2)
                fare_amount *= surge_multiplier
            
            # Tip - more likely with higher fare, better service
            tip_amount = 0.0
            tip_probability = 0.25 + (fare_amount / 100) * 0.3  # Higher fare = more likely to tip
            tip_probability = min(0.65, tip_probability)  # Cap at 65%
            
            if random.random() < tip_probability:
                # Tip percentage: 10-25% of fare
                tip_percentage = np.random.uniform(0.10, 0.25)
                tip_amount = round(fare_amount * tip_percentage, 2)
                # Round to nearest 0.50 or whole dollar
                if tip_amount < 1:
                    tip_amount = round(tip_amount * 2) / 2
                else:
                    tip_amount = round(tip_amount)
            
            # Ride status - most completed, some cancelled
            ride_status = random.choices(
                ["completed", "cancelled", "in_progress"],
                weights=[0.94, 0.05, 0.01]
            )[0]
            
            # Only completed rides have dropoff data
            if ride_status != "completed":
                dropoff_datetime = None
                dropoff_lat = None
                dropoff_lon = None
                fare_amount = 0.0
                tip_amount = 0.0
            
            rides.append({
                "ride_id": f"RIDE{day:03d}{i:05d}",
                "driver_id": driver_id,
                "passenger_id": passenger_id,
                "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "dropoff_datetime": dropoff_datetime.strftime("%Y-%m-%d %H:%M:%S") if dropoff_datetime else None,
                "pickup_latitude": round(pickup_lat, 6),
                "pickup_longitude": round(pickup_lon, 6),
                "dropoff_latitude": round(dropoff_lat, 6) if dropoff_lat else None,
                "dropoff_longitude": round(dropoff_lon, 6) if dropoff_lon else None,
                "fare_amount": round(fare_amount, 2),
                "tip_amount": round(tip_amount, 2),
                "surge_multiplier": surge_multiplier,
                "ride_status": ride_status
            })
    
    return pd.DataFrame(rides)


def add_data_quality_issues(df, issue_rate=0.02):
    """Add some data quality issues for testing"""
    num_issues = int(len(df) * issue_rate)
    
    # Add some nulls
    null_indices = np.random.choice(df.index, size=num_issues, replace=False)
    for idx in null_indices[:num_issues//3]:
        col = random.choice(["fare_amount", "pickup_latitude", "driver_id"])
        if col in df.columns:
            df.at[idx, col] = None
    
    # Add some invalid coordinates
    for idx in null_indices[num_issues//3:2*num_issues//3]:
        if "pickup_latitude" in df.columns:
            df.at[idx, "pickup_latitude"] = np.random.uniform(-100, 100)  # Invalid
    
    # Add some negative fares
    for idx in null_indices[2*num_issues//3:]:
        if "fare_amount" in df.columns and df.at[idx, "fare_amount"] is not None:
            df.at[idx, "fare_amount"] = -abs(df.at[idx, "fare_amount"])
    
    return df


def main():
    """Generate all sample data"""
    print("Generating realistic sample data...")
    print(f"📅 Generating rides for date: {CURRENT_DATE.strftime('%Y-%m-%d')}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate drivers
    print(f"Generating {NUM_DRIVERS} drivers...")
    drivers_df = generate_drivers(NUM_DRIVERS)
    drivers_df.to_csv(OUTPUT_DIR / "drivers.csv", index=False)
    print(f"✓ Drivers saved to {OUTPUT_DIR / 'drivers.csv'}")
    print(f"  - Active drivers: {drivers_df['is_active'].sum()}")
    print(f"  - Avg rating: {drivers_df['rating'].mean():.2f}")
    
    # Generate passengers
    print(f"\nGenerating {NUM_PASSENGERS} passengers...")
    passengers_df = generate_passengers(NUM_PASSENGERS)
    passengers_df.to_csv(OUTPUT_DIR / "passengers.csv", index=False)
    print(f"✓ Passengers saved to {OUTPUT_DIR / 'passengers.csv'}")
    print(f"  - Avg rating: {passengers_df['rating'].mean():.2f}")
    
    # Generate rides
    print(f"\nGenerating {NUM_RIDES} rides...")
    rides_df = generate_rides(NUM_RIDES, drivers_df, passengers_df)
    
    # Add some data quality issues
    rides_df = add_data_quality_issues(rides_df, issue_rate=0.02)
    
    # Save rides by date
    rides_df["pickup_date"] = pd.to_datetime(rides_df["pickup_datetime"]).dt.date
    for date, group in rides_df.groupby("pickup_date"):
        date_str = date.strftime("%Y-%m-%d")
        date_dir = OUTPUT_DIR / "rides" / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        group.drop("pickup_date", axis=1).to_csv(date_dir / "rides.csv", index=False)
        print(f"✓ Rides for {date_str} saved ({len(group)} records)")
    
    print("\n✅ Sample data generation complete!")
    print(f"\nData summary:")
    print(f"  - Drivers: {len(drivers_df)}")
    print(f"  - Passengers: {len(passengers_df)}")
    print(f"  - Total Rides: {len(rides_df)}")
    completed_rides = rides_df[rides_df['ride_status'] == 'completed']
    print(f"  - Completed Rides: {len(completed_rides)}")
    if len(completed_rides) > 0:
        print(f"  - Avg Fare: ${completed_rides['fare_amount'].mean():.2f}")
        print(f"  - Avg Tip: ${completed_rides['tip_amount'].mean():.2f}")
        # Calculate average distance for completed rides
        distances = []
        for idx, row in completed_rides.iterrows():
            if pd.notna(row['dropoff_latitude']) and pd.notna(row['dropoff_longitude']):
                dist = haversine_distance(
                    row['pickup_latitude'], row['pickup_longitude'],
                    row['dropoff_latitude'], row['dropoff_longitude']
                )
                distances.append(dist)
        if distances:
            print(f"  - Avg Distance: {np.mean(distances):.2f} km")
    print(f"  - Date range: {rides_df['pickup_datetime'].min()} to {rides_df['pickup_datetime'].max()}")


if __name__ == "__main__":
    main()
