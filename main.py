import logging
import orjson
from websocket_server import WebsocketServer
from datetime import datetime
import time
import flask
import threading


logging.basicConfig(
  level = logging.DEBUG,
  format = '[%(asctime)s] [%(levelname)s] %(message)s',
  datefmt = '%Y/%m/%d %I:%M:%S'
)

host = "0.0.0.0"
port = 8011
server = WebsocketServer(host=host, port=port, loglevel=logging.DEBUG)

drones = {}

def handle_drone_connect(client, server):
    print(f"Client connected : {client['id']}")


def handle_drone_message(client, server, message):
    data = orjson.loads(message)
    timestamp = data["timestamp"] 
    drone_name = data["drone_name"]

    if data["type"] == "init":
        drones[drone_name] = {}
        drones[drone_name]["drone_info"] = data["drone_info"]
        drones[drone_name]["client"] = client
        drones[drone_name]["drone_status"] = {}
        print(f"Drone Connected : {drone_name}\nInfo : {data['drone_info']}")
    elif data["type"] == "status":
        drones[drone_name]["drone_status"] = data["drone_status"]
        print(f"Drone Status Recive : {drone_name}\nStaus : {data['drone_status']}")

app = flask.Flask(__name__)

@app.route("/")
def root():
    return flask.redirect("/drones_status")

@app.route("/debug_consle")
def deubg_console():
    return flask.render_template("debugConsole.html")

@app.route("/drones_status")
def drones_status():
    data = {}
    for i in drones.keys():
        data[i] = {}
        data[i]["status"] = drones[i]["drone_status"]
        data[i]["info"] = drones[i]["drone_info"]
    return flask.jsonify(data)

@app.route("/send_command" , methods= ["GET","POST"])
def send_command():
    data = flask.request.json
    name = data["name"]
    command = data["command"]
    parameter = data["parameter"]
    data = {
        "type" : "command",
        "timestamp" : datetime.now(),
        "command" : command,
        "parameter" : parameter
    }
    server.send_message(drones[name]["client"],orjson.dumps(data,option=orjson.OPT_NAIVE_UTC))
    return "Command execute success"


def run_flask_server():
    app.run(host="0.0.0.0",port=8012)

def run_websocket_server():
    server.set_fn_new_client(handle_drone_connect)
    server.set_fn_message_received(handle_drone_message)
    server.run_forever()

if __name__ == "__main__":

    
    websocket_thread = threading.Thread(target=run_websocket_server)
    websocket_thread.start()

    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.start()
