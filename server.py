#!/usr/bin/env python3
from flask import Flask, send_file, redirect, request, jsonify, session, make_response, Response
import uuid
from flask_socketio import SocketIO
from collections import defaultdict
import json
import random
import time
import threading

app = Flask(__name__, static_folder="public/")

app.secret_key = "correcthorsebatterystaple"

socketio = SocketIO(app)

games = {}

participants = defaultdict(set)

leaderboards = defaultdict(dict)

seeds = {}

names = {}

creators = {}

running = set()

times = defaultdict(lambda: float("inf"))

end_times = defaultdict(lambda: float("inf"))

@app.route("/")
def index_route():
    return redirect("/public/index.html")

@app.route("/login", methods=["POST"])
def login_route():
    """
    Set username, must be called before connecting to anything
    """
    if "id" not in session.keys():
        session["id"] = str(uuid.uuid4())
    names[session["id"]] = request.form.get("name")
    return redirect("/public/index.html")

@app.route("/create", methods=["POST"])
def create_route():
    if "id" not in session.keys():
        return Response("Error: must log in first", status=400, mimetype='text/plain')
    user_id = session["id"]
    game_id = str(uuid.uuid4())
    games[game_id] = request.form.get("name")
    creators[game_id] = user_id
    participants[game_id] = set()
    if "time" in request.form.keys():
        # time in seconds that game should last
        try:
            times[game_id] = float(request.form.get("time"))
        except:
            times[game_id] = float("inf")
    else:
        times[game_id] = float("inf")
    return redirect("/public/index.html")

@app.route("/list", methods=["GET"])
def list_route():
    return jsonify(games)

@app.route("/seeds", methods=["GET"])
def seeds_route():
    return jsonify(seeds)

@app.route("/my_game", methods=["GET"])
def my_game_route():
    try:
        game_id = session["game_id"]
    except:
        return ""
    if game_id in running:
        return jsonify({"game_id": game_id, "running": True, "seed": seeds[game_id], "latestProblemDone": leaderboards[game_id][session["id"]]["latestProblemDone"], "endTime": end_times[game_id]})
    else:
        return jsonify({"game_id": game_id, "running": False})

@app.route("/my_name", methods=["GET"])
def my_name_route():
    try:
        return names[session["id"]]
    except:
        return ""

@app.route("/join", methods=["POST"])
def join_route():
    if "id" not in session.keys() or session["id"] not in names:
        return Response("{'status': 'error', 'message': 'must log in first'}", status=400, mimetype='application/json')
    game_id = request.get_json()["game_id"]
    session["game_id"] = game_id
    for game in participants:
        try:
            participants[game].remove(session["id"])
        except:
            pass
    participants[game_id].add(session["id"])
    leaderboards[game_id][session["id"]] = {"score": 0, "numCorrect": 0, "latestProblemDone": 0, "timeStarted": 0}
    socketio.emit('join', json.dumps({"game_id": session["game_id"], "user": session["id"]}), namespace="/game")
    return jsonify({'status': 'success', 'game_id': game_id})

@app.route("/leave", methods=["POST"])
def leave_route():
    game_id = session["game_id"]
    try:
        participants[game_id].remove(session["id"])
        leaderboards[game_id].pop(session["id"])
    except:
        pass
    session.pop("game_id")
    return jsonify({'status': 'success', 'user_id': session["id"]})

@app.route("/delete", methods=["DELETE"])
def delete_route():
    if "id" not in session.keys():
        return Response("{'status': 'error', 'message': 'must log in first'}", status=400, mimetype='application/json')
    user_id = session["id"]
    game_id = request.get_json()["id"]
    try:
        if user_id != creators[game_id]:
            return jsonify({'status': 'error', 'message': 'you didn\'t create the game'})
    except:
        return Response("{'status': 'error', 'message': 'game has no creator'}", status=400, mimetype='application/json')
    try:
        games.pop(game_id)
    except:
        pass
    try:
        participants.pop(game_id)
    except:
        pass
    try:
        leaderboards.pop(game_id)
    except:
        pass
    try:
        creators.pop(game_id)
    except:
        pass
    try:
        running.remove(game_id)
    except:
        pass
    try: end_times.pop(game_id)
    except KeyError: pass
    try: times.pop(game_id)
    except KeyError: pass
    return jsonify({'status': 'success', 'game_id': game_id})

@app.route("/participants", methods=["GET"])
def participants_route():
    return jsonify({k: list(v) for k, v in participants.items()})

@app.route("/names", methods=["GET"])
def names_route():
    return jsonify(names)

@app.route("/leaderboard", methods=["GET"])
def leaderboard_route():
    return jsonify(leaderboards[session["game_id"]])

@socketio.on('connect', namespace='/game')
def connect():
    print(f'Client connected')

@socketio.on('disconnect', namespace='/game')
def disconnect():
    print(f'Client disconnected')

def end_game(game_id: str):
    try: running.remove(game_id)
    except KeyError: pass
    try: end_times.pop(game_id)
    except KeyError: pass
    try: times.pop(game_id)
    except KeyError: pass
    socketio.emit('end', json.dumps({"game_id": game_id}), namespace="/game")

@socketio.on('start', namespace='/game')
def handle_start():
    if session["game_id"] in running:
        return
    if creators[session["game_id"]] != session["id"]:
        return
    running.add(session["game_id"])
    seed = random.random()
    seeds[session["game_id"]] = seed
    end_times[session["game_id"]] = times[session["game_id"]] + time.time()
    socketio.emit('start', json.dumps({"game_id": session["game_id"], "seed": seed, "endTime": end_times[session["game_id"]]}), namespace="/game")

@socketio.on('solve', namespace='/game')
def handle_solve(data):
    if session["game_id"] not in running:
        return
    j = json.loads(data)
    game_id = session["game_id"]
    leaderboards[game_id][session["id"]]["score"] += j["points"]
    leaderboards[game_id][session["id"]]["numCorrect"] += 1 if not j["skip"] else 0
    leaderboards[game_id][session["id"]]["latestProblemDone"] = j["latestProblemDone"]
    leaderboards[game_id][session["id"]]["timeStarted"] = time.time()
    socketio.emit('solve', json.dumps({"game_id": session["game_id"], "user_id": session["id"], "numCorrect": leaderboards[game_id][session["id"]]["numCorrect"], "score": leaderboards[game_id][session["id"]]["score"]}), namespace="/game")

def end_checker(hz = 2):
    while True:
        for game_id in list(end_times.keys()):
            if time.time() >= end_times[game_id]:
                end_game(game_id)
        time.sleep(1 / hz)

def create_app():
    checker = threading.Thread(target=end_checker, daemon=True)
    checker.start()
    return app

if __name__ == "__main__":
    checker = threading.Thread(target=end_checker, daemon=True)
    checker.start()
    socketio.run(app, host="0.0.0.0", port=8080)