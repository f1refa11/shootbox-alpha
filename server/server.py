import socket
import os
import json
import random
import threading

BUFFERSIZE = 512

outgoing = []

class Player:
	def __init__(self, ownerid):
		self.x = 64
		self.y = 64
		self.ownerid = ownerid
		self.initHp = 100
		self.hp = 100

playerMap = {}

print("""
####################

ShootBox Server v0.5

####################
""")
rootPath = os.path.dirname(__file__)
with open(os.path.join(rootPath, "config.json")) as f:
	config = json.load(f)
try:
	with open("map.json") as f:
		serverMap = json.load(f)
except FileNotFoundError:
	serverMap = []
	for block in range(random.randint(2, int(config["size"][0])-2)):
		randomPos = [random.randint(0,16), random.randint(0,16)]
		serverMap.append(
			{"block": "tree", "pos": [randomPos[0], randomPos[1]]}
		)

def createServer(port, maxPlayers=99):
	global serv
	serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serv.bind(('', port))
	serv.listen(maxPlayers)

def listenClients():
	while 1:
		conn, addr = serv.accept()  # начинаем принимать соединения
		print('connected:', addr)  # выводим информацию о подключении
		conn.send(bytes(json.dumps({"size": [512, 512], "yourPos": [64, 64]}), encoding = 'UTF-8'))
		data = conn.recv(1024)  # принимаем данные от клиента, по 1024 байт
		print(str(data))
		# conn.send(data.upper())

def destroyServer():
	serv.close()

createServer(1234, 8)
bob = threading.Thread(target=listenClients)
# bob.setDaemon(True)
bob.start()