from flask import Blueprint, jsonify, request
from datetime import datetime
import random

ambulance_bp = Blueprint('ambulance', __name__)

def sim():
    from app import simulator
    return simulator

HISTORY = [
    {"id":"AMB_001","date":"2024-11-01","time":"08:22","from":"AIIMS","to":"Safdarjung","eta_sec":55,"response_sec":48,"cleared":True,"ml_confidence":0.97,"method":"YOLO+Siren+Beacon"},
    {"id":"AMB_002","date":"2024-11-03","time":"14:10","from":"RML Hospital","to":"GTB Hospital","eta_sec":70,"response_sec":65,"cleared":True,"ml_confidence":0.94,"method":"YOLO+Siren"},
    {"id":"AMB_003","date":"2024-11-05","time":"19:45","from":"Apollo","to":"LNJP","eta_sec":40,"response_sec":38,"cleared":True,"ml_confidence":0.96,"method":"YOLO+Siren+Beacon"},
    {"id":"AMB_004","date":"2024-11-07","time":"02:30","from":"Max Hospital","to":"Trauma Centre","eta_sec":90,"response_sec":78,"cleared":False,"ml_confidence":0.89,"method":"YOLO"},
    {"id":"AMB_005","date":"2024-11-09","time":"11:05","from":"Moolchand","to":"AIIMS","eta_sec":50,"response_sec":45,"cleared":True,"ml_confidence":0.98,"method":"YOLO+Siren+Beacon"},
    {"id":"AMB_006","date":"2024-11-12","time":"16:30","from":"Fortis","to":"RML Hospital","eta_sec":60,"response_sec":55,"cleared":True,"ml_confidence":0.93,"method":"YOLO+Siren"},
    {"id":"AMB_007","date":"2024-11-15","time":"09:15","from":"LNJP","to":"Safdarjung","eta_sec":35,"response_sec":32,"cleared":True,"ml_confidence":0.99,"method":"YOLO+Siren+Beacon"},
    {"id":"AMB_008","date":"2024-11-18","time":"22:50","from":"GTB Hospital","to":"AIIMS","eta_sec":80,"response_sec":72,"cleared":True,"ml_confidence":0.91,"method":"YOLO"},
    {"id":"AMB_009","date":"2024-11-21","time":"07:10","from":"Safdarjung","to":"Apollo","eta_sec":45,"response_sec":42,"cleared":True,"ml_confidence":0.95,"method":"YOLO+Beacon"},
    {"id":"AMB_010","date":"2024-11-25","time":"18:33","from":"AIIMS","to":"Max Hospital","eta_sec":65,"response_sec":60,"cleared":True,"ml_confidence":0.97,"method":"YOLO+Siren+Beacon"},
]

ML_MODELS = [
    {"model":"YOLOv8n","accuracy":0.94,"detection_ms":28,"type":"Visual Detection","samples":12000},
    {"model":"Siren Audio CNN","accuracy":0.91,"detection_ms":150,"type":"Audio (800-1200Hz)","samples":8500},
    {"model":"Beacon Detector","accuracy":0.96,"detection_ms":12,"type":"Flash Rate (1-3Hz)","samples":5000},
    {"model":"Ensemble Model","accuracy":0.98,"detection_ms":190,"type":"Combined All","samples":25500},
]

@ambulance_bp.route('/trigger', methods=['POST'])
def trigger():
    data = request.get_json() or {}
    frm = data.get('from', 'AIIMS Hospital')
    to  = data.get('to', 'Safdarjung Hospital')
    eta = data.get('eta_seconds', random.randint(40,90))
    s = sim()
    amb = s.trigger_ambulance(frm, to, eta)
    from app import socketio
    socketio.emit('ambulance_alert', {
        "ambulance_id": amb["id"],
        "message": "AMBULANCE DETECTED — CLEAR THE LANE NOW!",
        "route": f"{frm} → {to}",
        "eta_seconds": amb["eta_seconds"],
        "ml_confidence": amb["ml_confidence"],
        "detection_method": amb["detection_method"],
        "timestamp": datetime.now().isoformat(),
    })
    return jsonify({"success": True, "data": amb})

@ambulance_bp.route('/status')
def status():
    s = sim()
    return jsonify({"active": s.ambulance_active, "data": s.ambulance})

@ambulance_bp.route('/clear', methods=['POST'])
def clear():
    sim().clear_ambulance()
    from app import socketio
    socketio.emit('ambulance_cleared', {"msg": "Ambulance cleared."})
    return jsonify({"success": True})

@ambulance_bp.route('/history')
def history():
    return jsonify(HISTORY)

@ambulance_bp.route('/ml-models')
def ml_models():
    return jsonify(ML_MODELS)
