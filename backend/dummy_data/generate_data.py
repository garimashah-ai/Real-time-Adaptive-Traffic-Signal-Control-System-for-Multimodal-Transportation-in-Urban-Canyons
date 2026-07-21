"""
Generate all dummy CSV data files.
Run: python generate_data.py
"""
import csv, random, os
from datetime import datetime, timedelta

os.makedirs("output", exist_ok=True)

INTERSECTIONS = ["I1","I2","I3","I4","I5","I6","I7","I8"]
REASONS = ["High vehicle volume","Signal malfunction","Road construction",
           "Accident reported","VIP convoy","Festival crowd","Waterlogging","Bus breakdown"]
VEHICLES = ["Car","Bus","Truck","Motorcycle","Auto-rickshaw","Taxi"]
HOSPITALS = ["AIIMS","Safdarjung","RML Hospital","GTB Hospital","Apollo","Max Hospital","LNJP","Fortis"]

def gen_traffic_log():
    rows = []
    base = datetime.now() - timedelta(days=7)
    for i in range(7*24*12):
        ts = base + timedelta(minutes=i*5)
        for iid in INTERSECTIONS:
            vc = random.randint(5,95)
            lvl = "Low" if vc<25 else "Medium" if vc<60 else "High"
            rows.append({"timestamp":ts.strftime("%Y-%m-%d %H:%M"),"intersection_id":iid,
                "vehicle_count":vc,"congestion_level":lvl,
                "clearance_time_min":random.randint(1,40),
                "avg_speed_kmh":round(max(5,70-vc*0.6),1),
                "reason":random.choice(REASONS) if lvl!="Low" else "Normal flow",
                "signal":random.choice(["Red","Green","Yellow"])})
    with open("output/traffic_log.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"✅ traffic_log.csv — {len(rows)} records")

def gen_yolo_detections():
    rows = []
    for i in range(1000):
        vt = random.choice(VEHICLES)
        rows.append({"frame_id":i,"vehicle_id":f"VEH_{i:04d}","type":vt,
            "confidence":round(random.uniform(0.72,0.99),3),
            "speed_kmh":round(random.uniform(0,65),1),
            "is_emergency":False,"intersection":random.choice(INTERSECTIONS)})
    for j in range(20):
        rows.append({"frame_id":9000+j,"vehicle_id":f"AMB_{j:03d}","type":"Ambulance",
            "confidence":round(random.uniform(0.89,0.99),3),
            "speed_kmh":round(random.uniform(50,85),1),
            "is_emergency":True,"intersection":random.choice(INTERSECTIONS)})
    with open("output/yolo_detections.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"✅ yolo_detections.csv — {len(rows)} records")

def gen_ambulance_history():
    rows = []
    base = datetime.now() - timedelta(days=30)
    for i in range(50):
        frm, to = random.sample(HOSPITALS, 2)
        eta = random.randint(30,120)
        rows.append({"incident_id":f"AMB_{100+i}",
            "date":(base+timedelta(days=random.randint(0,30))).strftime("%Y-%m-%d"),
            "time":f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
            "from":frm,"to":to,"eta_sec":eta,
            "response_sec":random.randint(max(20,eta-15),eta+10),
            "route_cleared":random.choices([True,False],[85,15])[0],
            "ml_confidence":round(random.uniform(0.85,0.99),2),
            "detection_method":random.choice(["YOLO","YOLO+Siren","YOLO+Siren+Beacon"])})
    with open("output/ambulance_history.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"✅ ambulance_history.csv — {len(rows)} records")

if __name__ == "__main__":
    print("Generating dummy data...")
    gen_traffic_log()
    gen_yolo_detections()
    gen_ambulance_history()
    print("\n🎉 Done! Check output/ folder.")
