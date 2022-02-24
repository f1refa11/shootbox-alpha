## -*- coding: utf-8 -*-

#Импортируем все библиотеки
import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *
import json
import random
import math
import socket
import threading
#Инициализируем и настраиваем Pygame
pygame.init()

# Показываем экран(не работает)

# isLoading = True

# screen = pygame.display.set_mode((1024, 576), pygame.RESIZABLE)
# pygame.display.set_caption("ShootBox - Loading...")
pygame.mouse.set_visible(False)
# textRenderer = pygame.font.Font(None, 24)
# loadingText = textRenderer.render("Loading", False, (255, 255, 255))
# loadingText_rect = loadingText.get_rect()
# loadingText_rect.center = screen.get_rect().center

# def loadingScreenDisplay():
# 	while isLoading:
# 		screen.fill((11, 9, 24))
# 		screen.blit(loadingText, loadingText_rect)

# 		# pygame.display.update()

# loadingDisplayThread = threading.Thread(target=loadingScreenDisplay)
# loadingDisplayThread.setDaemon(True)
# loadingDisplayThread.start()

screen = pygame.display.set_mode((1024, 576), pygame.RESIZABLE)
pygame.display.set_caption("ShootBox - Main Menu")
clock = pygame.time.Clock()
gameSurface = pygame.Surface((1024, 1024))
gameSurface_Rect = gameSurface.get_rect()
gameSurface_Rect.x = 0
gameSurface_Rect.y = 0
guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
guiSurface.convert_alpha()
	
#Работаем над директориями
rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")

texturesPath = os.path.join(resourcesPath, "textures")
soundsPath = os.path.join(resourcesPath, "sounds")
musicPath = os.path.join(resourcesPath, "music")
langPath = os.path.join(resourcesPath, "lang")
mapPath = os.path.join(resourcesPath, "maps")

#Текстуры
skinTexturesPath = os.path.join(texturesPath, "skins")
guiTexturesPath = os.path.join(texturesPath, "gui")
itemTexturesPath = os.path.join(texturesPath, "item")
blocksTexturesPath = os.path.join(texturesPath, "blocks")

#Скины
defaultSkinPath = os.path.join(skinTexturesPath, "default")

#Загружаем все JSON файлы
with open(os.path.join(rootPath, "settings.json")) as f:
	settings = json.load(f)

with open(os.path.join(mapPath, "testMap.json")) as f:
	testMap = json.load(f)

#Импортируем шрифт
fonts = []
for x in range(1, 250):
	fonts.append(pygame.font.Font(os.path.join(resourcesPath, "font.ttf"), x))

quality = 0
nickname = "FireFall"
pressedKeys = {
	'right': False,
	'up': False,
	'left': False,
	'down': False
}
summonedCubes = []
cubeCooldown = random.randint(300, 500)
collisionRects = []
shotBullets = []
oldScreen = None

for l in range(len(testMap)):
	collisionRects.append(pygame.Rect(testMap[l]["pos"][0]*64, testMap[l]["pos"][1]*64, 64, 64))

#Настраиваем подключение
# connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# gamePort = 26675
# gameAddress = "192.168.1.70"
# connection.bind((gameAddress, gamePort))
# connection.listen()
# client, client_address = connection.accept()

availableResolutions = [
	(1366, 768),
	(1360, 768),
	(1280, 720),
	(1024, 768),
	(1024, 576),
	(960, 720),
	(960, 600),
	(960, 540),
	(928, 696),
	(896, 672),
	(864, 486),
	(840, 525),
	(800, 600),
	(800, 512),
	(800, 450),
	(720, 450),
	(720, 405),
	(700, 525),
]


cursor = pygame.image.load(os.path.join(guiTexturesPath, "cursor.png"))
cursor = pygame.transform.smoothscale(cursor, (2**(5+quality), 2**(5+quality)))
cursor = pygame.transform.smoothscale(cursor, (64, 64)).convert_alpha()

gunCursor = pygame.image.load(os.path.join(guiTexturesPath, "gunCursor.png")).convert_alpha()
gunCursor = pygame.transform.smoothscale(gunCursor, (2**(5+quality), 2**(5+quality)))
gunCursor = pygame.transform.smoothscale(gunCursor, (64, 64)).convert_alpha()

woodPlanks = pygame.image.load(os.path.join(blocksTexturesPath, "woodPlanks.png"))
woodPlanks = pygame.transform.smoothscale(woodPlanks, (2**(5+quality), 2**(5+quality)))
woodPlanks = pygame.transform.smoothscale(woodPlanks, (64, 64)).convert_alpha()

tree = pygame.image.load(os.path.join(blocksTexturesPath, "tree.png"))
tree = pygame.transform.smoothscale(tree, (2**(5+quality), 2**(5+quality)))
tree = pygame.transform.smoothscale(tree, (64, 64)).convert_alpha()

hotBar = pygame.image.load(os.path.join(guiTexturesPath, "hotBar.png"))
hotBar = pygame.transform.smoothscale(hotBar, (2**(5+quality), 2**(5+quality)))
hotBar = pygame.transform.smoothscale(hotBar, (64, 64)).convert_alpha()

gunItem = pygame.image.load(os.path.join(itemTexturesPath, "gun.png"))
gunItem = pygame.transform.smoothscale(gunItem, (2**(5+quality), 2**(5+quality)))
gunItem = pygame.transform.smoothscale(gunItem, (64, 64)).convert_alpha()

inventoryGui = pygame.image.load(os.path.join(guiTexturesPath, "inventory.png"))
inventoryGui = pygame.transform.smoothscale(inventoryGui, (80*(2**quality), 2**(6+quality)))
inventoryGui = pygame.transform.smoothscale(inventoryGui, (640, 512))

logo = pygame.image.load(os.path.join(guiTexturesPath, "logo.png")).convert_alpha()

def renderText(text, size, color, dest=None, align=None):
	textSurface = fonts[size].render(text, True, color)
	textSurface_rect = textSurface.get_rect()
	if dest == "center":
		textSurface_rect.center = screen.get_rect().center
	if dest[0] == "center":
		textSurface_rect.centerx = screen.get_rect().centerx
	elif dest[0] == "right":
		textSurface_rect.x = screen.get_width()-textSurface_rect.w
	else:
		textSurface_rect.x = int(dest[0])
	if dest[1] == "center":
		textSurface_rect.centery = screen.get_rect().centery
	elif dest[1] == "bottom":
		textSurface_rect.y = screen.get_height()-textSurface_rect.h
	else:
		textSurface_rect.y = int(dest[1])
	guiSurface.blit(textSurface, textSurface_rect)

class Player(object):
	def __init__(self):
		self.defaultNormal = pygame.image.load(os.path.join(defaultSkinPath, "idle.png"))
		self.defaultNormal = pygame.transform.smoothscale(self.defaultNormal, (2**(5+quality), 2**(5+quality)))
		self.defaultNormal = pygame.transform.smoothscale(self.defaultNormal, (64, 64)).convert_alpha()

		self.defaultGunHold = pygame.image.load(os.path.join(defaultSkinPath, "gunHold.png"))
		self.defaultGunHold = pygame.transform.smoothscale(self.defaultGunHold, (2**(5+quality), 2**(5+quality)))
		self.defaultGunHold = pygame.transform.smoothscale(self.defaultGunHold, (64, 64)).convert_alpha()
		self.skin = "default"
		self.currentSkinTexture = None
		self.x = gameSurface.get_width()//2
		self.y = gameSurface.get_height()//2
		self.rect = pygame.Rect(self.x, self.y, availableResolutions[4][0]/32, 32)
		self.rect.center = guiSurface.get_rect().center
		self.speed = 3
		self.inventory = [
			{"item": "wood_planks", "amount": 64, "slot": 0},
			{"item": "gun", "slot": 1}
		]
		self.selectedSlot = 0
		self.skills = []
		self.initHp = 100
		self.hp = 100
		self.nicknameDisplay = fonts[24].render(nickname, True, (255, 255, 255))
		self.nicknameDisplay_rect = self.nicknameDisplay.get_rect()
		self.nicknameDisplay_rect.centerx = self.rect.centerx
		self.nicknameDisplay_rect.y = self.rect.y-32
		self.angle = None
		self.relX = None
		self.relY = None
	def checkForCollision(self):
		isCollision = False

		for x in range(len(collisionRects)):
			isCollision = False

			if self.rect.colliderect(collisionRects[x]):
				isCollision = True

			if isCollision == True:
					break

		return isCollision
	def moveLeft(self):
		global cameraX
		if not self.rect.left < 0:
			self.rect.x -= self.speed
			self.x -= self.speed
			gameSurface_Rect.x += self.speed
			if self.checkForCollision():
				self.rect.x += self.speed
				self.x += self.speed
				gameSurface_Rect.x -= self.speed
	def moveRight(self):
		global cameraX
		if not self.rect.right > gameSurface.get_width():
			self.rect.x += self.speed
			self.x += self.speed
			gameSurface_Rect.x -= self.speed
			if self.checkForCollision():
				self.rect.x -= self.speed
				self.x -= self.speed
				gameSurface_Rect.x += self.speed
	def moveUp(self):
		global cameraY
		if not self.rect.top < 0:
			self.rect.y -= self.speed
			self.y -= self.speed
			gameSurface_Rect.y += self.speed
			if self.checkForCollision():
				self.rect.y += self.speed
				self.y += self.speed
				gameSurface_Rect.y -= self.speed
	def moveDown(self):
		global cameraY
		if not self.rect.bottom > gameSurface.get_height():
			self.rect.y += self.speed
			self.y += self.speed
			gameSurface_Rect.y -= self.speed
			if self.checkForCollision():
				self.rect.y -= self.speed
				self.y -= self.speed
				gameSurface_Rect.y += self.speed
	def render(self):
		mouseX, mouseY = pygame.mouse.get_pos()
		self.oldCenter = self.rect.center
		for x in range(len(self.inventory)):
			if self.selectedSlot == self.inventory[x]["slot"]:
				if self.inventory[x]["item"] == "gun":
					self.currentSkinTexture = self.defaultGunHold
				else:
					self.currentSkinTexture = self.defaultNormal
			else:
				self.currentSkinTexture = self.defaultNormal
		self.angle = math.atan2(mouseY-screen.get_rect().centery, mouseX-screen.get_rect().centerx)
		self.angle = -math.degrees(self.angle)
		self.currentSkinTexture = pygame.transform.smoothscale(self.currentSkinTexture, (64, 64))
		self.currentSkinTexture = pygame.transform.rotozoom(self.currentSkinTexture, self.angle-90, 1)
		self.newRect = self.currentSkinTexture.get_rect()
		self.newRect.center = self.oldCenter
		gameSurface.blit(self.currentSkinTexture, self.newRect)
		self.nicknameDisplay_rect = self.nicknameDisplay.get_rect()
		self.nicknameDisplay_rect.centerx = self.rect.centerx
		self.nicknameDisplay_rect.y = self.rect.y-32
		gameSurface.blit(self.nicknameDisplay, self.nicknameDisplay_rect)

# class Bullet(object):
# 	def __init__(self, angle, x, y):
# 		self.angle = angle
# 		self.texture = [
# 			pygame.transform.rotozoom(pygame.transform.scale(pygame.image.load(os.path.join(itemTexturesPath, "bullet32.png")).convert_alpha(), (32, 16)), self.angle, 1),
# 			pygame.transform.rotozoom(pygame.transform.scale(pygame.image.load(os.path.join(itemTexturesPath, "bullet64.png")).convert_alpha(), (32, 16)), self.angle, 1),
# 			pygame.transform.rotozoom(pygame.transform.scale(pygame.image.load(os.path.join(itemTexturesPath, "bullet128.png")).convert_alpha(), (32, 16)), self.angle, 1),
# 			pygame.transform.rotozoom(pygame.transform.scale(pygame.image.load(os.path.join(itemTexturesPath, "bullet256.png")).convert_alpha(), (32, 16)), self.angle, 1),
# 			pygame.transform.rotozoom(pygame.transform.scale(pygame.image.load(os.path.join(itemTexturesPath, "bullet512.png")).convert_alpha(), (32, 16)), self.angle, 1),
# 			pygame.transform.rotozoom(pygame.transform.scale(pygame.image.load(os.path.join(itemTexturesPath, "bullet1024.png")).convert_alpha(), (32, 16)), self.angle, 1),
# 		]
# 		self.rect = self.texture.get_rect(center = (x, y))
# 		self.pos = (x, y)
# 	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
# 		self.move_vec = pygame.math.Vector2()
# 		self.move_vec.from_polar((speed, angle_in_degrees))
# 		return old_xy + self.move_vec
# 	def render(self):
# 		self.pos = self.calculate_new_xy(self.pos, 3, -self.angle)
# 		self.rect.center = round(self.pos[0])+16, round(self.pos[1])+8
# 		gameSurface.blit(self.texture, self.pos)

class Cube(object):
	def __init__(self):
		self.x = random.randint(0, screen.get_width())
		self.y = screen.get_width()-24
		self.size = random.randint(35,100)
		self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
		self.angle = 0
		self.rotateSpeed = random.uniform(0.1, 1.5)
		self.speed = random.randint(1, 4)
		self.transparency = random.randint(15, 150)
		self.rotateMode = random.randint(0,1)
		self.rectSurface = pygame.Surface((self.size, self.size), pygame.SRCALPHA).convert_alpha()
		self.rectSurface.fill((27, 18, 75))
		self.rect = self.rectSurface.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y
		self.rectSurface.set_colorkey((0,0,0))
		self.rectSurface.set_alpha(self.transparency)
	def render(self):
		self.rectSurface.fill((255, 255, 255))
		self.oldCenter = self.rect.center
		self.rotatedRectSurface = pygame.transform.rotate(self.rectSurface, self.angle)
		self.rect = self.rotatedRectSurface.get_rect()
		self.rect.center = self.oldCenter 
		guiSurface.blit(self.rotatedRectSurface, self.rect)
		if self.angle == 360:
			self.angle = 0
		else:
			if self.rotateMode == 0:
				self.angle += self.rotateSpeed
			else:
				self.angle -= self.rotateSpeed
		self.rect.y -= self.speed

class Button(object):
	def __init__(self, text, col, row):
		self.text = text
		self.col = col
		self.row = row
		self.textRenderer = fonts[24].render((str(self.text)), True, (255, 255, 255))
		self.textRenderer_rect = self.textRenderer.get_rect()

		self.textureDefault = pygame.image.load(os.path.join(guiTexturesPath, "buttonDefault.png"))
		self.textureDefault = pygame.transform.smoothscale(self.textureDefault, (2**(7+quality), 2**(7+quality)))
		self.textureDefault = pygame.transform.smoothscale(self.textureDefault, (256, 64)).convert_alpha()

		self.textureHovered = pygame.image.load(os.path.join(guiTexturesPath, "buttonHovered.png"))
		self.textureHovered = pygame.transform.smoothscale(self.textureHovered, (2**(7+quality), 2**(7+quality)))
		self.textureHovered = pygame.transform.smoothscale(self.textureHovered, (256, 64)).convert_alpha()

		self.state = "default"
		self.rect = pygame.Rect(0, 0, 256, 64)
		self.rect.centerx = gameSurface.get_width() // 2 + (128 * self.row)
		self.rect.y = 32+(self.col*64)
	def render(self):
		if self.rect.collidepoint(pygame.mouse.get_pos()):
			self.state = "hovered"
		else:
			self.state = "default"
		if self.state == "default":
			guiSurface.blit(self.textureDefault, self.rect)
		else:
			guiSurface.blit(self.textureHovered, self.rect)
		guiSurface.blit(self.textRenderer, (self.rect.centerx-self.textRenderer_rect.centerx, self.rect.centery-self.textRenderer_rect.centery-8))
		self.rect.centerx = screen.get_width()/2 + (128 * self.row)

player = Player()

playButton = Button("Играть", 2, 0)
settingsButton = Button("Настройки", 3, -1)
exitButton = Button("Выход", 3, 1)

# gameSurface_Rect.x = 
isLoading = False

def menu():
	last = pygame.time.get_ticks()
	global cubeCooldown
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			summonedCubes.append(Cube())
			cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.remove(summonedCubes[i])
					i -= 1
			except IndexError:
				pass
			i += 1

		playButton.render()
		settingsButton.render()
		exitButton.render()

		guiSurface.blit(logo, (screen.get_width()/2-224, 48))

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if playButton.rect.collidepoint(event.pos):
						game()
					if settingsButton.rect.collidepoint(event.pos):
						gameSettings()
					if exitButton.rect.collidepoint(event.pos):
						pygame.quit()
						sys.exit()
		
		renderText("version: 0.3", 12, (255, 255, 255), ("center", "bottom"))

		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def gameSettings():
	last = pygame.time.get_ticks()
	global cubeCooldown
	pygame.display.set_caption("ShootBox - Settings")
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))


		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			summonedCubes.append(Cube())
			cubeCooldown = random.randint(300, 500)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.remove(summonedCubes[i])
					i -= 1
			except IndexError:
				pass
			i += 1

		screen.blit(cursor, pygame.mouse.get_pos())
		
		pygame.display.update()

def game():
	pygame.display.set_caption("ShootBox - Game")
	global quality, screen, guiSurface, gameSurface, gameSurface_Rect
	last = pygame.time.get_ticks()
	# for x in range(random.randint(2, 15)):
	# 	randomPos = [random.randint(0,16), random.randint(0,16)]
	# 	testMap.append(
	# 		{"block": "tree", "pos": [randomPos[0], randomPos[1]]}
	# 	)
	# 	collisionRects.append(pygame.Rect(randomPos[0]*64+24, randomPos[1]*64+24, 16, 16))
	# print(collisionRects)

	while 1:
		clock.tick(60)
		screen.fill((42, 170, 255))
		gameSurface.fill((29, 189, 104))
		guiSurface.fill((0,0,0,0))
		
		oldScreen = [screen.get_width(), screen.get_height()]
		# oldGameSurface = [gameSurface.get_width(), gameSurface.get_height()]

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_w:
					pressedKeys["up"] = True
				elif event.key == K_s:
					pressedKeys["down"] = True
				elif event.key == K_a:
					pressedKeys["left"] = True
				elif event.key == K_d:
					pressedKeys["right"] = True
			elif event.type == KEYUP:
				if event.key == K_w:
					pressedKeys["up"] = False
				elif event.key == K_s:
					pressedKeys["down"] = False
				elif event.key == K_a:
					pressedKeys["left"] = False
				elif event.key == K_d:
					pressedKeys["right"] = False
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 3:
					for i in range(len(player.inventory)):
						if player.selectedSlot == player.inventory[i]["slot"]:
							if player.inventory[i]["item"] == "gun":
								pass
							elif player.inventory[i]["item"] == "wood_planks":
								if player.inventory[i]["amount"] != 0:
									if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
										sameBlock = False
										for x in range(len(testMap)):
											sameBlock = False
											if testMap[x]["pos"] == [(event.pos[0]-gameSurface_Rect.x)//64, (event.pos[1]-gameSurface_Rect.y)//64]:
												sameBlock = True
												break
											
										if not sameBlock:
											collisionRects.append(pygame.Rect((event.pos[0]-gameSurface_Rect.x)//64*64, (event.pos[1]-gameSurface_Rect.y)//64*64, 64, 64))
											testMap.append({"block": "wood_planks", "pos": [(event.pos[0]-gameSurface_Rect.x)//64, (event.pos[1]-gameSurface_Rect.y)//64]})
											player.inventory[i]["amount"] -= 1
										if player.rect.colliderect(collisionRects[-1]):
											collisionRects.remove(pygame.Rect((event.pos[0]-gameSurface_Rect.x)//64*64, (event.pos[1]-gameSurface_Rect.y)//64*64, 64, 64))
											testMap.pop(-1)
											player.inventory[i]["amount"] += 1
				if event.button == 1:
					for x in range(len(player.inventory)):
						if player.selectedSlot == player.inventory[x]["slot"]:
							if player.inventory[x]["item"] == "gun":
								# shotBullets.append(Bullet(player.angle, player.rect.x, player.rect.y))
								pass
						else:
							i = 0
							while i <= len(testMap):
								try:
									if testMap[i]["pos"] == [(event.pos[0]-gameSurface_Rect.x)//64, (event.pos[1]-gameSurface_Rect.y)//64]:
										if testMap[i]['block'] == "wood_planks":
											collisionRects.remove(pygame.Rect((event.pos[0]-gameSurface_Rect.x)//64*64, (event.pos[1]-gameSurface_Rect.y)//64*64, 64, 64))
											testMap.pop(i)
											i -= 1
										elif testMap[i]["block"] == "tree":
											collisionRects.remove(pygame.Rect((event.pos[0]-gameSurface_Rect.x)//64*64+24, (event.pos[1]-gameSurface_Rect.y)//64*64+24, 16, 16))
											testMap.pop(i)
											i -= 1
								except IndexError:
									pass
								except ValueError:
									pass
								i += 1
									
				if event.button == 4:
					if player.selectedSlot == 7:
						player.selectedSlot = 0
					else:
						player.selectedSlot += 1
				if event.button == 5:
					if player.selectedSlot == 0:
						player.selectedSlot = 7
					else:
						player.selectedSlot -= 1
			elif event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
				gameSurface_Rect.x += ( screen.get_width() - oldScreen[0])//2
				gameSurface_Rect.y += ( screen.get_height() - oldScreen[1])//2

		if pressedKeys["up"]:
			player.moveUp()
		if pressedKeys["down"]:
			player.moveDown()
		if pressedKeys["left"]:
			player.moveLeft()
		elif pressedKeys["right"]:
			player.moveRight()

		for b in range(len(testMap)):
			if testMap[b]["block"] == "wood_planks":
				gameSurface.blit(woodPlanks, (testMap[b]["pos"][0]*64, testMap[b]["pos"][1]*64))

		i = 0
		while i <= len(shotBullets):
			try:
				shotBullets[i].render()
				if not gameSurface.get_rect().colliderect(shotBullets[i].rect):
					shotBullets.remove(shotBullets[i])
					i -= 1
			except IndexError:
				pass
			i += 1
		player.render()

		for b in range(len(testMap)):
			if testMap[b]["block"] == "tree":
				gameSurface.blit(tree, (testMap[b]["pos"][0]*64, testMap[b]["pos"][1]*64))

		s = 0
		c = 0
		if len(collisionRects) > 0:
			if len(shotBullets) > 0:
				while c <= len(collisionRects):
					while s < len(shotBullets):
						if collisionRects[c].colliderect(shotBullets[s].rect):
							shotBullets.remove(shotBullets[s])
							s -= 1
						s += 1
					c += 1

		for h in range(8):
			guiSurface.blit(hotBar, (guiSurface.get_width()//2-256+h*64, guiSurface.get_height()-64))
		for x in range(len(player.inventory)):
			if player.inventory[x]["item"] == "gun":
				guiSurface.blit(gunItem, (guiSurface.get_width()//2-256+player.inventory[x]["slot"]*64, guiSurface.get_height()-64))
			if player.inventory[x]["item"] == "wood_planks":
				if player.inventory[x]["amount"] != 0:
					guiSurface.blit(pygame.transform.smoothscale(woodPlanks, (48, 48)), (guiSurface.get_width()//2-256+player.inventory[x]["slot"]*64+8, guiSurface.get_height()-64+8))
					renderText(str(player.inventory[x]["amount"]), 16, (255, 255, 255), (guiSurface.get_width()//2-256+player.inventory[x]["slot"]*64+32, guiSurface.get_height()-64+32))
		pygame.draw.rect(guiSurface, (255, 0, 0), (guiSurface.get_width()//2-256+player.selectedSlot*64, guiSurface.get_height()-64, 64, 64), 3)

		for x in range(len(player.inventory)):
			if player.selectedSlot == player.inventory[x]["slot"]:
				if player.inventory[x]["item"] == "gun":
					guiSurface.blit(gunCursor, (pygame.mouse.get_pos()[0]-32, pygame.mouse.get_pos()[1]-32))
				else:
					guiSurface.blit(cursor, pygame.mouse.get_pos())
			else:
				guiSurface.blit(cursor, pygame.mouse.get_pos())

		renderText("FPS: "+str(int(clock.get_fps())), 36, (255, 255, 255), (5,5))

		screen.blit(gameSurface, gameSurface_Rect)
		screen.blit(guiSurface, (0,0))

		pygame.display.update()

menu()