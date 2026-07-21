from flask import Blueprint, jsonify
traffic_bp = Blueprint('traffic', __name__)

def sim():
    from app import simulator
    return simulator

@traffic_bp.route('/status')
def status():
    return jsonify(sim().get_state())

@traffic_bp.route('/congestion-report')
def report():
    ints = list(sim().intersections.values())
    return jsonify({
        "high": [i for i in ints if i["congestion_level"]=="High"],
        "medium": [i for i in ints if i["congestion_level"]=="Medium"],
        "low": [i for i in ints if i["congestion_level"]=="Low"],
        "avg_clearance": round(sum(i["clearance_time_min"] for i in ints)/len(ints), 1),
    })

@traffic_bp.route('/network')
def network():
    from utils.traffic_simulator import ROADS
    s = sim()
    return jsonify({
        "nodes": [{"id":k,"name":v["name"],"lat":v["lat"],"lng":v["lng"],
                   "congestion":v["congestion_level"],"vehicles":v["vehicle_count"]}
                  for k,v in s.intersections.items()],
        "edges": [{"from":a,"to":b} for a,b in ROADS]
    })
