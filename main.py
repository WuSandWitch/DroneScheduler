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
port = 19999
server = WebsocketServer(host=host, port=port, loglevel=logging.DEBUG)

drones = {}

def handle_drone_connect(client, server):
    logging.info(f"Client connected : {client['id']}")


def handle_drone_message(client, server, message):
    data = orjson.loads(message)
    timestamp = data["timestamp"] 
    drone_name = data["drone_name"]

    if data["type"] == "init":
        drones[drone_name] = {}
        drones[drone_name]["drone_info"] = data["drone_info"]
        drones[drone_name]["client"] = client
        drones[drone_name]["drone_status"] = {}
        command_thread.start()
        logging.info(f"Drone Connected : {drone_name}\nInfo : {data['drone_info']}")
    elif data["type"] == "status":
        drones[drone_name]["drone_status"] = data["drone_status"]
        logging.info(f"Drone Status Recive : {drone_name}\nStaus : {data['drone_status']}")

app = flask.Flask(__name__)
@app.route("/drones_status")
def drones_status():
    data = {}
    for i in drones.keys():
        data[i] = {}
        data[i]["status"] = drones[i]["drone_status"]
        data[i]["info"] = drones[i]["drone_info"]
    return flask.jsonify(data)

def run_flask_server():
    app.run(host="0.0.0.0",port=8080)

def run_websocket_server():
    server.set_fn_new_client(handle_drone_connect)
    server.set_fn_message_received(handle_drone_message)
    server.run_forever()

def send_command():
    while True:
        name = "test drone1"
        command = "test"
        data = {
            "type" : "command",
            "timestamp" : datetime.now(),
            "command" : command,
            "parameter" : {
                "test para1" : "test",
                "test para2" : "test"
            }
        }
        logging.info("Send command: ",data)
        time.sleep(5)
        server.send_message(drones[name]["client"],orjson.dumps(data,option=orjson.OPT_NAIVE_UTC))

if __name__ == "__main__":

    
    websocket_thread = threading.Thread(target=run_websocket_server)
    websocket_thread.start()

    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.start()

    command_thread = threading.Thread(target=send_command)
    # command_thread.start()
