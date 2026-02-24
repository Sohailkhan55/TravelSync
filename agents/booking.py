import random
from datetime import datetime, timedelta

class MockTravelService:
    def search_flights(self, origin, destination, date):
        """
        Returns mock flight options.
        """
        airlines = ["IndiGo", "Air India", "Vistara", "Akasa Air"]
        flights = []
        
        for _ in range(3):
            dept_hour = random.randint(6, 20)
            dept_time = datetime.strptime(f"{date} {dept_hour}:00", "%Y-%m-%d %H:%M")
            duration = random.randint(90, 180) # minutes
            arrival_time = dept_time + timedelta(minutes=duration)
            
            flights.append({
                "airline": random.choice(airlines),
                "flight_number": f"IN-{random.randint(100, 999)}",
                "departure": dept_time.strftime("%H:%M"),
                "arrival": arrival_time.strftime("%H:%M"),
                "price": random.randint(3000, 12000),
                "currency": "INR"
            })
            
        return sorted(flights, key=lambda x: x['price'])

    def search_trains(self, origin, destination, date):
        """
        Returns mock train options.
        """
        trains = [
            {"name": "Vande Bharat Express", "code": "20901", "type": "Premium"},
            {"name": "Rajdhani Express", "code": "12951", "type": "Premium"},
            {"name": "Shatabdi Express", "code": "12009", "type": "Premium"},
            {"name": "Intercity Express", "code": "19035", "type": "Standard"}
        ]
        
        results = []
        for _ in range(3):
            train = random.choice(trains)
            dept_hour = random.randint(5, 22)
            results.append({
                "train_name": train["name"],
                "train_number": train["code"],
                "departure": f"{dept_hour}:00",
                "duration": f"{random.randint(4, 12)}h",
                "price_3A": random.randint(800, 2000),
                "price_2A": random.randint(1500, 3500),
                "currency": "INR"
            })
            
        return results

def get_travel_options(origin, destination, date):
    service = MockTravelService()
    return {
        "flights": service.search_flights(origin, destination, date),
        "trains": service.search_trains(origin, destination, date)
    }
