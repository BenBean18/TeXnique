#!/usr/bin/env python3
from flask import Flask, send_file, redirect, request, jsonify, session, make_response, Response
import uuid
from flask_socketio import SocketIO
from collections import defaultdict
import json
import random

app = Flask(__name__, static_folder="public/")

app.secret_key = "correcthorsebatterystaple"

socketio = SocketIO(app)

games = {}

participants = defaultdict(set)

leaderboards = defaultdict(dict)

names = {}

running = set()

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
    game_id = str(uuid.uuid4())
    games[game_id] = request.form.get("name")
    return redirect("/")

@app.route("/list", methods=["GET"])
def list_route():
    return jsonify(games)

@app.route("/my_game", methods=["GET"])
def my_game_route():
    try:
        return session["game_id"]
    except:
        return ""

@app.route("/my_name", methods=["GET"])
def my_name_route():
    try:
        return names[session["id"]]
    except:
        return ""

@app.route("/join", methods=["POST"])
def join_route():
    if "id" not in session.keys():
        return Response("{'status': 'error', 'message': 'must log in first'}", status=400, mimetype='application/json')
    game_id = request.get_json()["game_id"]
    session["game_id"] = game_id
    participants[game_id].add(session["id"])
    leaderboards[game_id][session["id"]] = 0
    return jsonify({'status': 'success', 'game_id': games[game_id]})

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
    game_id = request.get_json()["id"]
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
        running.remove(session["game_id"])
    except:
        pass
    return jsonify({'status': 'success', 'game_id': game_id})

@app.route("/participants", methods=["GET"])
def participants_route():
    return jsonify(participants)

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

@socketio.on('start', namespace='/game')
def handle_start():
    if session["game_id"] in running:
        return
    running.add(session["game_id"])
    socketio.emit('start', json.dumps({"game_id": session["game_id"], "seed": random.random()}), namespace="/game")

@socketio.on('solve', namespace='/game')
def handle_solve(data):
    j = json.loads(data)
    game_id = session["game_id"]
    leaderboards[game_id][session["id"]] = {"score": j["score"], "numCorrect": j["numCorrect"]}
    socketio.emit('solve', json.dumps({"game_id": session["game_id"], "user_id": session["id"], "numCorrect": j["numCorrect"], "score": j["score"]}), namespace="/game")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)