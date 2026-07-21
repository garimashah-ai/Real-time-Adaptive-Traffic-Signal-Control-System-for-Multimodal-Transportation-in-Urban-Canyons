import random, time
from datetime import datetime

INTERSECTIONS = [
    {"id":"I1","name":"Connaught Place – Janpath","lat":28.6315,"lng":77.2167},
    {"id":"I2","name":"Karol Bagh – Pusa Road","lat":28.6514,"lng":77.1907},
    {"id":"I3","name":"Lajpat Nagar – Ring Road","lat":28.5677,"lng":77.2434},
    {"id":"I4","name":"Nehru Place – MB Road","lat":28.5491,"lng":77.2518},
    {"id":"I5","name":"Dwarka Sec-10 Crossing","lat":28.5820,"lng":77.0500},
    {"id":"I6","name":"Rohini – Pitampura Chowk","lat":28.7041,"lng":77.1025},
    {"id":"I7","name":"ITO – Vikas Marg","lat":28.6289,"lng":77.2405},
    {"id":"I8","name":"Azadpur – GTK Road","lat":28.7165,"lng":77.1799},
]

ROADS = [("I1","I2"),("I1","I7"),("I2","I6"),("I3","I4"),
         ("I4","I7"),("I5","I2"),("I6","I8"),("I7","I8"),("I3","I7"),("I2","I7")]

REASONS = ["High vehicle volume","Signal malfunction","Road construction",
           "Accident reported","VIP convoy","Festival crowd",
           "Waterlogging","Bus breakdown","School dismissal","Market congestion"]

VEHICLE_TYPES = ["Car","Bus","Truck","Motorcycle","Auto-rickshaw","Taxi"]

YOLO_HISTORY = [
    {"frame":1001,"type":"Car","conf":0.97,"speed":32,"emergency":False},
    {"frame":1002,"type":"Bus","conf":0.94,"speed":18,"emergency":False},
    {"frame":1003,"type":"Truck","conf":0.91,"speed":22,"emergency":False},
    {"frame":1004,"type":"Motorcycle","conf":0.88,"speed":45,"emergency":False},
    {"frame":1005,"type":"Ambulance","conf":0.98,"speed":67,"emergency":True},
    {"frame":1006,"type":"Car","conf":0.95,"speed":28,"emergency":False},
    {"frame":1007,"type":"Auto-rickshaw","conf":0.89,"speed":25,"emergency":False},
    {"frame":1008,"type":"Taxi","conf":0.93,"speed":35,"emergency":False},
]

class TrafficSimulator:
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.intersections = {}
        self.ambulance_active = False
        self.ambulance = {}
        self._init()

    def _congestion(self, vc):
        if vc < 25: return "Low", random.randint(1,5)
        elif vc < 60: return "Medium", random.randint(6,15)
        else: return "High", random.randint(16,40)

    def _init(self):
        for i in INTERSECTIONS:
            vc = random.randint(10,90)
            cong, clear = self._congestion(vc)
            self.intersections[i["id"]] = {
                **i,
                "vehicle_count": vc,
                "congestion_level": cong,
                "clearance_time_min": clear,
                "avg_speed_kmh": round(max(5, 70-vc*0.6), 1),
                "reason": random.choice(REASONS),
                "signal": random.choice(["Red","Green","Yellow"]),
                "yolo_sample": random.sample(YOLO_HISTORY, 4),
                "updated": datetime.now().isoformat(),
            }

    def _update(self):
        for k, v in self.intersections.items():
            vc = max(0, min(100, v["vehicle_count"] + random.randint(-6,8)))
            cong, clear = self._congestion(vc)
            v.update({
                "vehicle_count": vc,
                "congestion_level": cong,
                "clearance_time_min": clear,
                "avg_speed_kmh": round(max(5, 70-vc*0.6), 1),
                "reason": random.choice(REASONS) if random.random()<0.05 else v["reason"],
                "signal": random.choices(["Red","Green","Yellow"],[40,50,10])[0],
                "yolo_sample": random.sample(YOLO_HISTORY, 4),
                "updated": datetime.now().isoformat(),
            })

    def trigger_ambulance(self, frm, to, eta=60):
        self.ambulance_active = True
        self.ambulance = {
            "id": f"AMB_{random.randint(100,999)}",
            "from": frm, "to": to,
            "eta_seconds": eta,
            "speed_kmh": random.randint(50,90),
            "ml_confidence": round(random.uniform(0.88,0.99), 2),
            "detection_method": "YOLOv8 + Siren Audio CNN + Beacon Detector",
            "triggered_at": datetime.now().isoformat(),
        }
        return self.ambulance

    def clear_ambulance(self):
        self.ambulance_active = False
        self.ambulance = {}

    def get_state(self):
        return {
            "intersections": list(self.intersections.values()),
            "roads": [{"from":a,"to":b} for a,b in ROADS],
            "ambulance_active": self.ambulance_active,
            "ambulance": self.ambulance,
            "total_vehicles": sum(v["vehicle_count"] for v in self.intersections.values()),
            "timestamp": datetime.now().isoformat(),
        }

    def run(self):
        while True:
            self._update()
            if self.socketio:
                self.socketio.emit('traffic_update', self.get_state())
                if self.ambulance_active and self.ambulance:
                    eta = self.ambulance.get("eta_seconds", 0)
                    if eta > 0:
                        self.ambulance["eta_seconds"] = max(0, eta-5)
                    else:
                        self.clear_ambulance()
                        self.socketio.emit('ambulance_cleared', {"msg":"Ambulance passed."})
            time.sleep(5)
