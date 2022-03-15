# -*- coding: utf-8 -*-

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
import pickle
import logging
import threading
import glob
pygame.init()

isLoading = True

screen = pygame.display.set_mode((1024, 576), pygame.RESIZABLE)
pygame.display.set_caption("ShootBox - Loading...")
pygame.mouse.set_visible(False)

rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")

loadingState = "Подготовка..."

textRenderer = pygame.font.Font(os.path.join(resourcesPath, "font.ttf"), 36)

def loadingScreenDisplay():
	while isLoading:
		screen.fill((11, 9, 24))
		loadingText = textRenderer.render(loadingState, False, (255, 255, 255))
		loadingText_rect = loadingText.get_rect()
		loadingText_rect.center = screen.get_rect().center
		screen.blit(loadingText, loadingText_rect)

		pygame.display.update()

loadingDisplayThread = threading.Thread(target=loadingScreenDisplay)
loadingDisplayThread.setDaemon(True)
loadingDisplayThread.start()
with open(os.path.join(rootPath, "config.json")) as f:
	config = json.load(f)

# screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

screen = pygame.display.set_mode((1024, 576), pygame.RESIZABLE)
pygame.display.set_caption("ShootBox - Main Menu")
clock = pygame.time.Clock()
guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
guiSurface.convert_alpha()
	
worldsPath = os.path.join(rootPath, "worlds")

texturesPath = os.path.join(resourcesPath, "textures")
soundsPath = os.path.join(resourcesPath, "sounds")
musicPath = os.path.join(resourcesPath, "music")
langPath = os.path.join(resourcesPath, "lang")
mapPath = os.path.join(resourcesPath, "maps")

skinTexturesPath = os.path.join(texturesPath, "skins")
guiTexturesPath = os.path.join(texturesPath, "gui")
itemTexturesPath = os.path.join(texturesPath, "item")
blocksTexturesPath = os.path.join(texturesPath, "blocks")

defaultSkinPath = os.path.join(skinTexturesPath, "default")

gameMap = []

fonts = []
for x in range(1, 250):
	fonts.append(pygame.font.Font(os.path.join(resourcesPath, "font.ttf"), x))

quality = 5
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
pauseMenu = False
oldScreen = None
blockDestroyTime = 0

for l in gameMap:
	collisionRects.append(pygame.Rect(l["pos"][0]*64, l["pos"][1]*64, 64, 64))

#Настраиваем подключение
# connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# gamePort = 26675
# gameAddress = "192.168.1.70"
# connection.bind((gameAddress, gamePort))
# connection.listen()
# client, client_address = connection.accept()

loadingState = "Загрузка текстур..."

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
# inventoryGui = pygame.transform.smoothscale(inventoryGui, (80*(2**quality), 2**(6+quality)))
scalingIndex = inventoryGui.get_height() / (screen.get_height()-8)
inventoryGui = pygame.transform.smoothscale(inventoryGui, (inventoryGui.get_width()/scalingIndex, screen.get_height()-8))
inventoryGui_rect = inventoryGui.get_rect()
inventoryGui_rect.center = screen.get_rect().center

buttonDefault = pygame.image.load(os.path.join(guiTexturesPath, "buttonDefault.png"))
buttonDefault = pygame.transform.smoothscale(buttonDefault, (2**(7+quality), 2**(7+quality)))
buttonDefault = pygame.transform.smoothscale(buttonDefault, (256, 64)).convert_alpha()

buttonHovered = pygame.image.load(os.path.join(guiTexturesPath, "buttonHovered.png"))
buttonHovered = pygame.transform.smoothscale(buttonHovered, (2**(7+quality), 2**(7+quality)))
buttonHovered = pygame.transform.smoothscale(buttonHovered, (256, 64)).convert_alpha()

dropDownDefault = pygame.image.load(os.path.join(guiTexturesPath, "dropDown.png"))
dropDownDefault = pygame.transform.smoothscale(dropDownDefault, (2**(7+quality), 2**(7+quality)))
dropDownDefault = pygame.transform.smoothscale(dropDownDefault, (256, 64)).convert_alpha()

dropDownOpened = pygame.image.load(os.path.join(guiTexturesPath, "dropDownOpened.png"))
dropDownOpened = pygame.transform.smoothscale(dropDownOpened, (2**(7+quality), 2**(7+quality)))
dropDownOpened = pygame.transform.smoothscale(dropDownOpened, (256, 64)).convert_alpha()

textInputTexture = pygame.image.load(os.path.join(guiTexturesPath, "input.png"))
textInputTexture = pygame.transform.smoothscale(textInputTexture, (2**(7+quality), 2**(7+quality)))
textInputTexture = pygame.transform.smoothscale(textInputTexture, (256, 64)).convert_alpha()


destroyBlock = []
for load in range(12):
	texture = pygame.image.load(os.path.join(blocksTexturesPath, "blockDestroy_"+str(load)+".png"))
	texture = pygame.transform.smoothscale(texture, (2**(5+quality), 2**(5+quality)))
	texture = pygame.transform.smoothscale(texture, (64, 64)).convert_alpha()
	destroyBlock.append(texture)

del texture

logo = pygame.image.load(os.path.join(guiTexturesPath, "logo.png")).convert_alpha()

# Грузим миры
savedWorlds = []
for world in glob.glob(os.path.join(worldsPath, "*.json")):
	try:
		with open(os.path.join(worldsPath, world), encoding="utf-8") as f:
			savedWorlds.append(json.load(f))
	except IsADirectoryError:
		pass

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
		self.rect = pygame.Rect(self.x+28, self.y+28, 36, 36)
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

		for rect in collisionRects:
			isCollision = False

			if self.rect.colliderect(rect):
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
		for x in self.inventory:
			if self.selectedSlot == x["slot"]:
				if x["item"] == "gun":
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

class Cube:
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

class Button:
	def __init__(self, text, col, row):
		self.text = text
		self.col = col
		self.row = row
		self.textRenderer = fonts[24].render((str(self.text)), True, (255, 255, 255))
		self.textRenderer_rect = self.textRenderer.get_rect()

		self.state = "default"
		self.rect = pygame.Rect(0, 0, 256, 64)
		self.rect.centerx = guiSurface.get_width() // 2 + (128 * self.row)
		self.rect.y = 32+(self.col*64)
	def render(self):
		if self.rect.collidepoint(pygame.mouse.get_pos()):
			self.state = "hovered"
		else:
			self.state = "default"
		if self.state == "default":
			guiSurface.blit(buttonDefault, self.rect)
		else:
			guiSurface.blit(buttonHovered, self.rect)
		guiSurface.blit(self.textRenderer, (self.rect.centerx-self.textRenderer_rect.centerx, self.rect.centery-self.textRenderer_rect.centery-8))
		self.rect.centerx = screen.get_width()/2 + (128 * self.row)

class Dropdown:
	def __init__(self, title, list, x, y):
		self.title = title
		self.list = list
		self.itemsRects = []
		for item in range(1, len(self.list)):
			self.itemsRects.append(pygame.Rect(self.x, self.y+item*64, 256, 64))
		self.opened = False
	def switch(self):
		self.opened ^= False
	def render(self):
		if self.opened:
			guiSurface.blit(dropDownOpened, (self.x, self.y))
			for item in self.list:
				pygame.draw.rect(guiSurface, (255, 255, 255), (self.x, (self.y+64)+item*64, 256, 64))
				pygame.draw.rect(guiSurface, (0, 0, 0), (self.x, (self.y+64)+item*64, 256, 64), 3, 3)
				renderText(str(self.list[item]), 24, (0, 0, 0), (self.x+8, ((self.y+64)+item*64)))
		else:
			guiSurface.blit(dropDownDefault, (self.x, self.y))
class TextInput:
	def __init__(self, x, y, text="", placeholder=""):
		self.text = text
		self.active = False
		self.x = x
		self.y = y
		self.rect = pygame.Rect(x, y, 256, 64)
		self.placeholderText = placeholder
		self.text_surface = fonts[28].render(self.text, True, (0, 0, 0))
		self.text_surface_rect = pygame.Rect(x+8, y, self.text_surface.get_width(), self.text_surface.get_height())
		self.text_surface_rect.centery = self.rect.centery
		self.placeholder = fonts[28].render(self.placeholderText, True, (179, 179, 179))
		self.placeholder_rect = pygame.Rect(x+8, y, self.placeholder.get_width(), self.placeholder.get_height())
		self.placeholder_rect.centery = self.rect.centery
		self.lineRect = pygame.Rect((self.text_surface_rect.topright[0]+4, self.rect.y+4), (3, 56))
	def eventHandle(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				self.active = True
			else:
				self.active = False
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					if len(self.text) <= 12:
						try:
							self.text += event.unicode
						except:
							pass
				self.text_surface = fonts[28].render(self.text, True, (0, 0, 0))
				self.text_surface_rect = pygame.Rect(self.x+8, self.y, self.text_surface.get_width(), self.text_surface.get_height()-8)
				self.text_surface_rect.centery = self.rect.centery
				self.placeholder = fonts[28].render(self.placeholderText, True, (179, 179, 179))
				self.placeholder_rect = pygame.Rect(self.x+8, self.y, self.placeholder.get_width(), self.placeholder.get_height())
				self.placeholder_rect.centery = self.rect.centery
				self.lineRect = pygame.Rect((self.text_surface_rect.topright[0]+4, self.rect.y+4), (3, 56))
	def render(self):
		guiSurface.blit(textInputTexture, self.rect)
		if len(self.text) == 0:
			guiSurface.blit(self.placeholder, self.placeholder_rect)
		guiSurface.blit(self.text_surface, self.text_surface_rect)
		if self.active:
			pygame.draw.rect(guiSurface, (0, 0, 0), self.lineRect)
	def getInput(self):
		return self.text

# gameSurface_Rect.x = 
isLoading = False

def menu():
	last = pygame.time.get_ticks()
	global cubeCooldown

	# Кнопки
	play = Button("Играть", 2, 0)
	settings = Button("Настройки", 3, -1)
	exit = Button("Выход", 3, 1)

	logoAppearingSpeed = 5
	logoY = -logo.get_height()
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

		guiSurface.blit(logo, (screen.get_width()/2-224, logoY))

		logoY += logoAppearingSpeed
		if logoAppearingSpeed > 0:
			logoAppearingSpeed -= 0.09
		if logoAppearingSpeed < 0:
			logoAppearingSpeed = 0

		play.render()
		settings.render()
		exit.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if play.rect.collidepoint(event.pos):
						playmodeSelect()
					if settings.rect.collidepoint(event.pos):
						gameSettings()
					if exit.rect.collidepoint(event.pos):
						pygame.quit()
						sys.exit()
		
		renderText("version: 0.3", 12, (255, 255, 255), ("center", "bottom"))

		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def playmodeSelect():
	last = pygame.time.get_ticks()
	global cubeCooldown
	pygame.display.set_caption("ShootBox - Menu")

	singleplayer = Button("Одиночная игра", 2, -1)
	multiplayer = Button("Мультиплеер", 2, 1)
	back = Button("Назад", 3, 0)

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

		singleplayer.render()
		multiplayer.render()
		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if singleplayer.rect.collidepoint(event.pos):
						singleplayerWorldAction()
					if multiplayer.rect.collidepoint(event.pos):
						multiplayerAction()
					if back.rect.collidepoint(event.pos):
						menu()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def singleplayerWorldAction():
	last = pygame.time.get_ticks()
	global cubeCooldown
	load = Button("Загрузить", 2, -1)
	create = Button("Создать", 2, 1)
	back = Button("Назад", 3, 0)
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

		load.render()
		create.render()
		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if load.rect.collidepoint(event.pos):
						loadWorldMenu()
					if create.rect.collidepoint(event.pos):
						createWorldMenu()
					if back.rect.collidepoint(event.pos):
						playmodeSelect()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def multiplayerAction():
	last = pygame.time.get_ticks()
	global cubeCooldown
	join = Button("Войти", 2, -1)
	create = Button("Создать комнату", 2, 1)
	back = Button("Назад", 3, 0)
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

		join.render()
		create.render()
		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if join.rect.collidepoint(event.pos):
						joinMultiplayerMenu()
					if create.rect.collidepoint(event.pos):
						createWorldMenu()
					if back.rect.collidepoint(event.pos):
						playmodeSelect()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def joinServer(ip, port):
	pass

def joinMultiplayerMenu():
	last = pygame.time.get_ticks()
	global cubeCooldown
	ipInput = TextInput(100, 100, "", placeholder="IP")
	portInput = TextInput(100, 200, "26675", placeholder="Порт")
	join = Button("Присоединиться", 3, 0)
	back = Button("Назад", 4, 0)
	mousePressed = False
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

		join.render()
		back.render()

		ipInput.render()
		portInput.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			ipInput.eventHandle(event)
			portInput.eventHandle(event)
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					mousePressed = True
					if join.rect.collidepoint(event.pos):
						print(ipInput.text)
					elif back.rect.collidepoint(event.pos):
						multiplayerAction()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()


widthInput = TextInput(100, 100, "")
heightInput = TextInput(100, 200, "")

def loadWorldMenu():
	last = pygame.time.get_ticks()
	global cubeCooldown
	worldChoices = []
	for world in range(len(savedWorlds)):
		worldTitle = fonts[24].render(str(savedWorlds[world]["title"]), False, (255, 255, 255))
		worldTitle_rect = worldTitle.get_rect()

		worldJoinButton = pygame.Rect(0, 0, 64, 24)
		worldJoinTitle = fonts[12].render("Загрузить", False, (53, 151, 255))
		worldJoinTitle_rect = worldJoinTitle.get_rect()
		
		worldDeleteButton = pygame.Rect(0, 0, 64, 24)
		worldDeleteTitle = fonts[12].render("Удалить", False, (53, 151, 255))
		worldDeleteTitle_rect = worldDeleteTitle.get_rect()

		worldSurface = pygame.Surface((worldTitle.get_width()+worldJoinButton.w+worldDeleteButton.w, worldJoinButton.h+worldDeleteButton.h+4), pygame.SRCALPHA).convert_alpha()
		worldSurface_rect = worldSurface.get_rect()

		worldTitle_rect.centery = worldSurface_rect.h//2
		worldTitle_rect.x = 0
		worldJoinButton.topright = worldSurface_rect.topright
		worldDeleteButton.bottomright = worldSurface_rect.bottomright
		worldJoinTitle_rect.center = worldJoinButton.center
		worldDeleteTitle_rect.center = worldDeleteButton.center

		worldSurface_rect.centerx = screen.get_width()//2
		worldSurface_rect.y = 64+(world*64)

		worldJoinButton2 = pygame.Rect(0, 0, 64, 24)
		worldDeleteButton2 = pygame.Rect(0, 0, 64, 24)

		worldJoinButton2.topright = worldSurface_rect.topright
		worldDeleteButton2.bottomright = worldSurface_rect.bottomright

		worldChoices.append([worldTitle, worldTitle_rect, worldJoinButton, worldJoinButton2, worldJoinTitle, worldJoinTitle_rect, worldDeleteButton, worldDeleteButton2, worldDeleteTitle, worldDeleteTitle_rect, worldSurface, worldSurface_rect])
	back = Button("Назад", 4, 0)
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

		back.render()

		for choice in worldChoices:
			choice[10].blit(choice[0], choice[1])
			choice[10].blit(choice[4], choice[5])
			choice[10].blit(choice[8], choice[9])
			if choice[3].collidepoint(pygame.mouse.get_pos()):
				pygame.draw.rect(choice[10], (255, 255, 255), choice[2], 2)
			else:
				pygame.draw.rect(choice[10], (53, 151, 255), choice[2], 2)
			if choice[7].collidepoint(pygame.mouse.get_pos()):
				pygame.draw.rect(choice[10], (255, 255, 255), choice[6], 2)
			else:
				pygame.draw.rect(choice[10], (53, 151, 255), choice[6], 2)

			guiSurface.blit(choice[10], choice[11])

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					for x in range(len(worldChoices)):
						if worldChoices[x][3].collidepoint(pygame.mouse.get_pos()):
							loadMap(savedWorlds[x])
							singleplayerMode()
						if worldChoices[x][7].collidepoint(pygame.mouse.get_pos()):
							print("Функция ещё не сделана!!!")
			
		
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def createWorldMenu():
	last = pygame.time.get_ticks()
	global cubeCooldown
	pygame.display.set_caption("ShootBox - Menu")
	create = Button("Создать", 2, 0)
	back = Button("Назад", 4, 0)
	mousePressed = False
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
		create.render()
		back.render()

		widthInput.render()
		heightInput.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			widthInput.eventHandle(event)
			heightInput.eventHandle(event)
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					mousePressed = True
					if create.rect.collidepoint(event.pos):
						generateMap()
						singleplayerMode()
					elif back.rect.collidepoint(event.pos):
						singleplayerWorldAction()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def loadMap(world):
	global gameSurface, gameSurface_Rect, player, gameMap
	gameSurface = pygame.Surface((world["size"][0]*64, world["size"][1]*64)).convert_alpha()
	gameSurface_Rect = gameSurface.get_rect()
	gameSurface_Rect.x = 0
	gameSurface_Rect.y = 0
	gameMap = world["map"]
	for block in gameMap:
		collisionRects.append(pygame.Rect(block["pos"][0]*64, block["pos"][1]*64, 64, 64))
	player = Player()

def generateMap():
	global gameSurface, gameSurface_Rect, player
	gameSurface = pygame.Surface((int(widthInput.getInput())*64, int(heightInput.getInput())*64)).convert_alpha()
	gameSurface_Rect = gameSurface.get_rect()
	gameSurface_Rect.x = 0
	gameSurface_Rect.y = 0
	for block in range(random.randint(2, int(widthInput.text)-2)):
		randomPos = [random.randint(0,16), random.randint(0,16)]
		gameMap.append(
			{"block": "tree", "pos": [randomPos[0], randomPos[1]]}
		)
		collisionRects.append(pygame.Rect(randomPos[0]*64+24, randomPos[1]*64+24, 16, 16))
	player = Player()

def gameSettings():
	last = pygame.time.get_ticks()
	global cubeCooldown
	pygame.display.set_caption("ShootBox - Settings")
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

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					pass

		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		renderText("FPS: "+str(int(clock.get_fps())), 20, (255, 255, 255), (10,10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def singleplayerMode():
	pygame.display.set_caption("ShootBox - Game")
	global quality, screen, guiSurface, gameSurface, gameSurface_Rect, pauseMenu, blockDestroyTime, inventoryGui, inventoryGui_rect
	last = pygame.time.get_ticks()

	mousePressed = False

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
				elif event.key == K_e:
					pauseMenu = not pauseMenu
				elif event.key == K_1:
					player.selectedSlot = 0
				elif event.key == K_2:
					player.selectedSlot = 1
				elif event.key == K_3:
					player.selectedSlot = 2
				elif event.key == K_4:
					player.selectedSlot = 3
				elif event.key == K_5:
					player.selectedSlot = 4
				elif event.key == K_6:
					player.selectedSlot = 5
				elif event.key == K_7:
					player.selectedSlot = 6
				elif event.key == K_8:
					player.selectedSlot = 7
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
					mousePressed = "right"
				if event.button == 1:
					mousePressed = "left"
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
			elif event.type == MOUSEBUTTONUP:
				mousePressed = False
			elif event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
				gameSurface_Rect.x += ( screen.get_width() - oldScreen[0])//2
				gameSurface_Rect.y += ( screen.get_height() - oldScreen[1])//2
				scalingIndex = inventoryGui.get_height() / (screen.get_height()-8)
				inventoryGui = pygame.transform.smoothscale(inventoryGui, (inventoryGui.get_width()/scalingIndex, screen.get_height()-8))
				inventoryGui_rect = inventoryGui.get_rect()
				inventoryGui_rect.center = screen.get_rect().center

		if mousePressed == "right":
			now = pygame.time.get_ticks()
			if now - last >= 250:
				last = now
				for playerSlot in player.inventory:
					if player.selectedSlot == playerSlot["slot"]:
						if playerSlot["item"] == "gun":
							pass
						elif playerSlot["item"] == "wood_planks":
							if playerSlot["amount"] != 0:
								if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
									sameBlock = False
									for block in gameMap:
										sameBlock = False
										if block["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
											sameBlock = True
											break
										
									if not sameBlock:
										collisionRects.append(pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64))
										gameMap.append({"block": "wood_planks", "pos": [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]})
										playerSlot["amount"] -= 1
									if player.rect.colliderect(collisionRects[-1]):
										collisionRects.remove(pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64))
										gameMap.pop(-1)
										playerSlot["amount"] += 1
		elif mousePressed == "left":
			now = pygame.time.get_ticks()
			for slot in player.inventory:
				if player.selectedSlot == slot["slot"]:
					if slot["item"] == "gun":
						# shotBullets.append(Bullet(player.angle, player.rect.x, player.rect.y))
						pass
					else:
						if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
							i = 0
							while i <= len(gameMap):
								try:
									if gameMap[i]["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
										if now - last >= 250:
											last = now
											if blockDestroyTime < 11:
												blockDestroyTime += 1
										if blockDestroyTime >= 11:
											if gameMap[i]['block'] == "wood_planks":
												collisionRects.remove(pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64))
												gameMap.pop(i)
												i -= 1
												if slot["item"] == "wood_planks":
													slot["amount"] += 1
											elif gameMap[i]["block"] == "tree":
												collisionRects.remove(pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64+24, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64+24, 16, 16))
												gameMap.pop(i)
												i -= 1
											blockDestroyTime = 0
								except IndexError:
									pass
								except ValueError:
									pass
								i += 1
		else:
			blockDestroyTime = 0

		if pressedKeys["up"]:
			player.moveUp()
		if pressedKeys["down"]:
			player.moveDown()
		if pressedKeys["left"]:
			player.moveLeft()
		elif pressedKeys["right"]:
			player.moveRight()

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

		for b in gameMap:
			#Рендер блоков
			if b["block"] == "tree":
				gameSurface.blit(tree, (b["pos"][0]*64, b["pos"][1]*64))
			elif b["block"] == "wood_planks":
				gameSurface.blit(woodPlanks, (b["pos"][0]*64, b["pos"][1]*64))
			
			if mousePressed == "left":
				if b["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
					gameSurface.blit(destroyBlock[blockDestroyTime], (b["pos"][0]*64, b["pos"][1]*64))
			
			#Рендер квадрата
			if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
				if not config["highlightSurface"]:
					if gameMap[b]["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
						pygame.draw.rect(gameSurface, (255, 255, 255), (gameMap[b]["pos"][0]*64, gameMap[b]["pos"][1]*64, 64, 64), 3)
				else:
					pygame.draw.rect(gameSurface, (255, 255, 255), ((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), 2)

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
		for x in player.inventory:
			if x["item"] == "gun":
				guiSurface.blit(gunItem, (guiSurface.get_width()//2-256+x["slot"]*64, guiSurface.get_height()-64))
			if x["item"] == "wood_planks":
				if x["amount"] != 0:
					guiSurface.blit(pygame.transform.smoothscale(woodPlanks, (48, 48)), (guiSurface.get_width()//2-256+x["slot"]*64+8, guiSurface.get_height()-64+8))
					renderText(str(x["amount"]), 16, (255, 255, 255), (guiSurface.get_width()//2-256+x["slot"]*64+32, guiSurface.get_height()-64+32))
		pygame.draw.rect(guiSurface, (255, 0, 0), (guiSurface.get_width()//2-256+player.selectedSlot*64, guiSurface.get_height()-64, 64, 64), 3)

		if pauseMenu:
			guiSurface.blit(inventoryGui, inventoryGui_rect)
			guiSurface.blit(player.defaultNormal, (200, 200))

		for x in player.inventory:
			if player.selectedSlot == x["slot"]:
				if x["item"] == "gun":
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