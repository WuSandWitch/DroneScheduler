import socket
import json
from datetime import datetime 


bind_ip = "0.0.0.0"
bind_port = 19999

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((bind_ip,bind_port))
server.listen(5)
print(f"[*] Listening on {bind_ip}:{bind_port} ")

drones = {}

def handle_drone_connect():
    while True:
        client,addr = server.accept()
        
        drone_name,drone_info = client.recv(2048).decode().split("--")
        drones[drone_name] = json.loads(drone_info)
        drones[drone_name]["client"] = client
        drones[drone_name]["addr"] = addr

        print("Drone connected :",drone_name)
        import pprint
        pprint.pprint(drones[drone_name])


if __name__ == "__main__":

    while True:
        client,addr = server.accept()
        
        drone_name,drone_info = client.recv(2048).decode().split("--")
        drones[drone_name] = json.loads(drone_info.replace("'","\""))
        drones[drone_name]["client"] = client
        drones[drone_name]["addr"] = addr

        print("Drone connected :",drone_name)
        import pprint
        pprint.pprint(drones[drone_name])

        while True:
            

            time_stamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            command = input("input command:")
            data = {
                "position" : " test"
            }

            command_string = f"[{time_stamp}]{command}{data}"
            print(command_string)
            client.send(command_string.encode())
            status = client.recv(1024)
            print(f"Status : {status}")