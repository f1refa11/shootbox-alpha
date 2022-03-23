import socket
import os
import json
import asyncore
import random
import pickle

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
def updateWorld(message):
	arr = pickle.loads(message)
	print(str(arr))
	playerid = arr[1]
	x = arr[2]
	y = arr[3]

	if playerid == 0: return

	playerMap[playerid].x = x
	playerMap[playerid].y = y

	remove = []

	for i in outgoing:
		update = ['playerPos']

		for key, value in playerMap.items():
			update.append([value.ownerid, value.x, value.y])
		
		try:
			i.send(pickle.dumps(update))
		except Exception:
			remove.append(i)
			continue
		
		print ('sent update data')

		for r in remove:
			outgoing.remove(r)

class MainServer(asyncore.dispatcher):
	def __init__(self, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.bind(('', port))
		self.listen(10)
	def handle_accept(self):
		conn, addr = self.accept()
		print ('Connection address:' + addr[0] + " " + str(addr[1]))
		outgoing.append(conn)
		playerid = random.randint(1000, 1000000)
		playerminion = Player(playerid)
		playerMap[playerid] = playerminion
		conn.send(pickle.dumps(['idUpdate', playerid]))
		SecondaryServer(conn)

class SecondaryServer(asyncore.dispatcher_with_send):
	def handle_read(self):
		recievedData = self.recv(BUFFERSIZE)
		if recievedData:
			updateWorld(recievedData)
		else: self.close()

MainServer(4321)
asyncore.loop()