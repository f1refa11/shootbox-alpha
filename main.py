# -*- coding: utf-8 -*-
import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *
import json
import random
# import numpy
# import perlin_numpy
import math
import threading
import glob
import webbrowser
# import psutil
pygame.init()

isLoading = True

rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")
langPath = os.path.join(resourcesPath, "lang")
with open(os.path.join(rootPath, "config.json")) as f:
	config = json.load(f)
if config["lang"] == "en":
	with open(os.path.join(langPath, "en.json"), encoding='utf-8') as f:
		translate = json.load(f)
elif config["lang"] == "ru":
	with open(os.path.join(langPath, "ru.json"), encoding='utf-8') as f:
		translate = json.load(f)
pygame.display.set_caption("ShootBox - "+translate["loading"])
pygame.mouse.set_visible(False)

windowSize = ()
displayInfo = pygame.display.Info()
if config["windowFlags"]["fullscreen"]:
	windowFlags = pygame.FULLSCREEN
	windowSize = (displayInfo.current_w, displayInfo.current_h)
else:
	windowFlags = pygame.RESIZABLE
	windowSize = (config["resolution"][0], config["resolution"][1])
if config["windowFlags"]["acceleration"]:
	windowFlags = windowFlags | pygame.HWSURFACE | pygame.DOUBLEBUF
screen = pygame.display.set_mode(windowSize, windowFlags)

rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")

loadingState = translate["prepairing"]

textRenderer = pygame.font.Font(os.path.join(resourcesPath, "font.ttf"), 36)

loadingRect_base = pygame.Rect(screen.get_width()//2-200, screen.get_height()-88, 400, 24)
loadingRect = pygame.Rect(loadingRect_base.x+4, loadingRect_base.y+4, 69, 16)

clock = pygame.time.Clock()

def loadingScreenDisplay():
	global loadingRect
	while isLoading:
		screen.fill((11, 9, 24))
		clock.tick(30)
		loadingText = textRenderer.render(loadingState, False, (255, 255, 255))
		loadingText_rect = loadingText.get_rect()
		loadingText_rect.center = screen.get_rect().center
		screen.blit(loadingText, loadingText_rect)
		pygame.draw.rect(screen, (255, 255, 255), loadingRect_base, 2)
		loadingRect.w += 2
		pygame.draw.rect(screen, (255, 255, 255), loadingRect)

		pygame.display.update()

loadingDisplayThread = threading.Thread(target=loadingScreenDisplay)
loadingDisplayThread.setDaemon(True)
loadingDisplayThread.start()

# screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

# screen = pygame.display.set_mode((1024, 576), pygame.RESIZABLE)
guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
guiSurface.convert_alpha()

worldsPath = os.path.join(rootPath, "worlds")

texturesPath = os.path.join(resourcesPath, "textures")
soundsPath = os.path.join(resourcesPath, "sounds")
musicPath = os.path.join(resourcesPath, "music")
langPath = os.path.join(resourcesPath, "lang")

serverPath = os.path.join(rootPath, "server")

playerTexturesPath = os.path.join(texturesPath, "player")
guiTexturesPath = os.path.join(texturesPath, "gui")
itemTexturesPath = os.path.join(texturesPath, "item")
blocksTexturesPath = os.path.join(texturesPath, "blocks")

walkAnimationPath = os.path.join(playerTexturesPath, "walk")
walkGunAnimationPath = os.path.join(playerTexturesPath, "walk_gun")
breakAnimationPath = os.path.join(playerTexturesPath, "block_break")
breakGunAnimationPath = os.path.join(playerTexturesPath, "block_break_gun")


gameMap = []

fonts = []
for x in range(1, 250):
	fonts.append(pygame.font.Font(os.path.join(resourcesPath, "font.ttf"), x))

version = "0.2"
nickname = "Player"
pressedKeys = {
	"right": False,
	"up": False,
	"left": False,
	"down": False
}
summonedCubes = []
cubeCooldown = random.randint(300, 500)
collisionRects = []
shotBullets = []
itemsList = []
inventoryItems = []
oldScreen = None
blockDestroyTime = 0
isConnected = False
playerId = 0
mousePressed = False
animationFrame = 0
inventoryRects = []
mapData = {}
blocksOffsetX = 0
blocksOffsetY = 0
TREE = "tree"
WOODLOG = "wood_log"
WOODPLANKS = "wood_planks"
COBBLESTONE = "cobblestone"
AIR = "air"
GUN = "gun"
WATER = "water"
SAND = "sand"
COLLECTABLE_ITEMS = [WOODLOG, WOODPLANKS, COBBLESTONE]

generationBlocks = {TREE, AIR, AIR, AIR}

multiplayerList = []

# Настраиваем подключение
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

loadingRect.width += 58

loadingState = translate["texturesLoading"]

def reloadTextures(guiAntialias, textureAntialias):
	cursor = pygame.image.load(os.path.join(guiTexturesPath, "cursor.png"))
	gunCursor = pygame.image.load(os.path.join(guiTexturesPath, "gunCursor.png"))
	grass = pygame.image.load(os.path.join(blocksTexturesPath, "grass.png"))
	woodPlanks = pygame.image.load(os.path.join(blocksTexturesPath, "woodPlanks.png"))
	cobblestone = pygame.image.load(os.path.join(blocksTexturesPath, "cobblestone.png"))
	tree = pygame.image.load(os.path.join(blocksTexturesPath, "tree.png"))
	sand = pygame.image.load(os.path.join(blocksTexturesPath, "sand.png"))
	bow = pygame.image.load(os.path.join(itemTexturesPath, "bow.png"))
	hotBar = pygame.image.load(os.path.join(guiTexturesPath, "hotBar.png"))
	gunItem = pygame.image.load(os.path.join(itemTexturesPath, "gun.png"))
	woodLog = pygame.image.load(os.path.join(itemTexturesPath, "woodLog.png"))
	inventoryGui_source = pygame.image.load(os.path.join(guiTexturesPath, "inventory.png"))
	inventoryGui_cell_source = pygame.image.load(os.path.join(guiTexturesPath, "inventoryCell.png"))
	inventoryGui_greenCell_source = pygame.image.load(os.path.join(guiTexturesPath, "inventoryCellGreen.png"))
	inventoryGui_hotbar_source = pygame.image.load(os.path.join(guiTexturesPath, "inventoryHotbar.png"))
	inventoryScaleIndex = inventoryGui_source.get_height() / (screen.get_height()-8)
	buttonDefault = pygame.image.load(os.path.join(guiTexturesPath, "buttonDefault.png"))
	buttonHovered = pygame.image.load(os.path.join(guiTexturesPath, "buttonHovered.png"))
	dropDownDefault = pygame.image.load(os.path.join(guiTexturesPath, "dropDown.png"))
	dropDownOpened = pygame.image.load(os.path.join(guiTexturesPath, "dropDownOpened.png"))
	textInputTexture = pygame.image.load(os.path.join(guiTexturesPath, "input.png"))
	switchOn = pygame.image.load(os.path.join(guiTexturesPath, "switchOn.png"))
	switchOff = pygame.image.load(os.path.join(guiTexturesPath, "switchOff.png"))
	pauseMenu_source = pygame.image.load(os.path.join(guiTexturesPath, "pauseMenu.png"))
	pauseMenuScaleIndex = pauseMenu_source.get_height() / (screen.get_height()-8)
	discord = pygame.image.load(os.path.join(guiTexturesPath, "discord.png"))
	github = pygame.image.load(os.path.join(guiTexturesPath, "github.png"))
	healthBar = pygame.image.load(os.path.join(guiTexturesPath, "healthBar.png"))
	health = pygame.image.load(os.path.join(guiTexturesPath, "health.png"))
	spinboxUp = pygame.image.load(os.path.join(guiTexturesPath, "spinboxUp.png"))
	spinboxDown = pygame.image.load(os.path.join(guiTexturesPath, "spinboxDown.png"))	
	pauseMenu = None
	woodPlanks_item = None
	woodLog_item = None
	cobblestone_item = None
	walkAnimation = []
	walkGunAnimation = []
	blockBreakAnimation = []
	breakGunAnimation = []
	destroyBlock = []
	water = []
	if guiAntialias:
		method = getattr(pygame.transform, "smoothscale")
	else:
		method = getattr(pygame.transform, "scale")
	cursor = method(cursor, (64, 64)).convert_alpha()
	gunCursor = method(gunCursor, (64, 64)).convert_alpha()
	hotBar = method(hotBar, (64, 64)).convert_alpha()
	gunItem = method(gunItem, (64, 64)).convert_alpha()
	inventoryGui = method(inventoryGui_source, (inventoryGui_source.get_width()/inventoryScaleIndex, screen.get_height()-8)).convert_alpha()
	inventoryCell = method(inventoryGui_cell_source, (160//inventoryScaleIndex, 160//inventoryScaleIndex))
	inventoryCell_green = method(inventoryGui_greenCell_source, (160//inventoryScaleIndex, 160//inventoryScaleIndex))
	inventoryHotbar = method(inventoryGui_hotbar_source, (160//inventoryScaleIndex, 160//inventoryScaleIndex))
	buttonDefault = method(buttonDefault, (256, 64)).convert_alpha()
	buttonHovered = method(buttonHovered, (256, 64)).convert_alpha()
	dropDownDefault = method(dropDownDefault, (256, 64)).convert_alpha()
	dropDownOpened = method(dropDownOpened, (256, 64)).convert_alpha()
	textInputTexture = method(textInputTexture, (256, 64)).convert_alpha()
	switchOn = method(switchOn, (64, 32)).convert_alpha()
	switchOff = method(switchOff, (64, 32)).convert_alpha()
	pauseMenu = method(pauseMenu_source, (pauseMenu_source.get_width()/inventoryScaleIndex, screen.get_height()-8)).convert_alpha()
	discord = method(discord, (71, 55))
	github = method(github, (64, 64))
	healthBar = method(healthBar, (128, 16))
	health = method(health, (128, 16))
	spinboxUp = method(spinboxUp, (32, 32))
	spinboxDown = method(spinboxDown, (32, 32))
	if textureAntialias:
		method = getattr(pygame.transform, "smoothscale")
	else:
		method = getattr(pygame.transform, "scale")
	grass = method(grass, (64, 64)).convert_alpha()
	woodPlanks = method(woodPlanks, (64, 64)).convert_alpha()
	tree = method(tree, (64, 64)).convert_alpha()
	sand = method(sand, (64, 64)).convert_alpha()
	woodLog = method(woodLog, (64, 64)).convert_alpha()
	cobblestone = method(cobblestone, (64, 64)).convert_alpha()
	woodPlanks_item = method(woodPlanks, (48, 48)).convert_alpha()
	woodLog_item = method(woodLog, (48, 48)).convert_alpha()
	cobblestone_item = method(cobblestone, (48, 48)).convert_alpha()
	for playerTexture in glob.glob(os.path.join(walkAnimationPath, "*.png")):
		texture = pygame.image.load(playerTexture).convert_alpha()
		texture = method(texture, (64, 64))
		walkAnimation.append(texture)
	for playerTexture in glob.glob(os.path.join(walkGunAnimationPath, "*.png")):
		texture = pygame.image.load(playerTexture).convert_alpha()
		texture = method(texture, (64, 64))
		walkGunAnimation.append(texture)
	for playerTexture in glob.glob(os.path.join(breakAnimationPath, "*.png")):
		texture = pygame.image.load(playerTexture).convert_alpha()
		texture = method(texture, (64, 64))
		blockBreakAnimation.append(texture)
	for playerTexture in glob.glob(os.path.join(breakGunAnimationPath, "*.png")):
		texture = pygame.image.load(playerTexture).convert_alpha()
		texture = method(texture, (64, 64))
		breakGunAnimation.append(texture)
	for load in range(12):
		texture = pygame.image.load(os.path.join(blocksTexturesPath, "blockDestroy_"+str(load)+".png"))
		texture = method(texture, (64, 64)).convert_alpha()
		destroyBlock.append(texture)
	for load in range(30):
		texture = pygame.image.load(os.path.join(blocksTexturesPath, "water_"+str(load)+".png"))
		texture = method(texture, (64, 64)).convert_alpha()
		water.append(texture)

	globals().update(locals())

reloadTextures(config["enableAntialiasing"]["gui"], config["enableAntialiasing"]["other"])

logo = pygame.image.load(os.path.join(guiTexturesPath, "logo.png")).convert_alpha()

inventoryGui_rect = inventoryGui.get_rect()
inventoryGui_rect.center = screen.get_rect().center

for channel in range(pygame.mixer.get_num_channels()):
	pygame.mixer.Channel(channel).set_volume(config["sfx"]/100)

pygame.mixer.music.set_volume(config["music"]/100)

guiClick = pygame.mixer.Sound(os.path.join(soundsPath, "click.ogg"))
guiSwitch = pygame.mixer.Sound(os.path.join(soundsPath, "switch.ogg"))
footstepGrass = pygame.mixer.Sound(os.path.join(soundsPath, "footstepGrass.ogg"))
footstepWood = pygame.mixer.Sound(os.path.join(soundsPath, "footstepWood.ogg"))
spinboxScroll = pygame.mixer.Sound(os.path.join(soundsPath, "scroll.ogg"))

# Грузим миры
savedWorlds = []
for world in glob.glob(os.path.join(worldsPath, "*.json")):
	try:
		with open(os.path.join(worldsPath, world), encoding="utf-8") as f:
			savedWorlds.append(json.load(f))
	except IsADirectoryError:
		pass

loadingRect.width = 392

class Player(object):
	def __init__(self, x, y, id):
		self.defaultNormal = pygame.image.load(os.path.join(playerTexturesPath, "idle.png"))
		self.defaultGunHold = pygame.image.load(os.path.join(playerTexturesPath, "gunHold.png"))
		if config["enableAntialiasing"]["other"]:
			self.defaultNormal = pygame.transform.smoothscale(self.defaultNormal, (64, 64)).convert_alpha()
			self.defaultGunHold = pygame.transform.smoothscale(self.defaultGunHold, (64, 64)).convert_alpha()
		else:
			self.defaultNormal = pygame.transform.scale(self.defaultNormal, (64, 64)).convert_alpha()
			self.defaultGunHold = pygame.transform.scale(self.defaultGunHold, (64, 64)).convert_alpha()
		self.skin = "default"
		self.currentSkinTexture = None
		self.animation = None
		self.x = x
		self.y = y
		self.id = id
		self.rect = pygame.Rect(self.x+28, self.y+28, 36, 36)
		self.rect.center = self.x, self.y
		gameSurface_Rect.x -= self.x     
		gameSurface_Rect.y -= self.y
		self.speed = 3
		self.inventory = [
			{"item": WOODPLANKS, "amount": 64, "slot": 0},
			# {"item": GUN, "amount": 32, "slot": 1},
			# {"item": WOODPLANKS, "amount": 38, "row": 0, "col": 1}
		]
		self.selectedSlot = 0
		self.skills = []
		self.initHp = 100
		self.hp = 100
		self.nicknameDisplay = fonts[24].render(nickname, config["enableAntialiasing"]["font"], (255, 255, 255))
		self.nicknameDisplay_rect = self.nicknameDisplay.get_rect()
		self.nicknameDisplay_rect.centerx = self.rect.centerx
		self.nicknameDisplay_rect.y = self.rect.y-32
		self.angle = None
		self.relX = None
		self.relY = None
		self.animationTimeIndex = 0
	def checkForCollision(self):
		isCollision = False

		for rect in collisionRects:
			isCollision = False
			isWater = False
			self.speed = 3

			if self.rect.colliderect(rect[0]):
				if rect[1]:
					isCollision = True
				else:
					isWater = True

			if isCollision:
				self.speed = 3
				break
			if isWater:
				self.speed = 1
				break

		return isCollision
	def moveLeft(self):
		if not self.rect.left < 0:
			self.rect.x -= self.speed
			self.x -= self.speed
			gameSurface_Rect.x += self.speed
			if self.checkForCollision():
				self.rect.x += self.speed
				self.x += self.speed
				gameSurface_Rect.x -= self.speed
	def moveRight(self):
		if not self.rect.right > gameSurface.get_width():
			self.rect.x += self.speed
			self.x += self.speed
			gameSurface_Rect.x -= self.speed
			if self.checkForCollision():
				self.rect.x -= self.speed
				self.x -= self.speed
				gameSurface_Rect.x += self.speed
	def moveUp(self):
		if not self.rect.top < 0:
			self.rect.y -= self.speed
			self.y -= self.speed
			gameSurface_Rect.y += self.speed
			if self.checkForCollision():
				self.rect.y += self.speed
				self.y += self.speed
				gameSurface_Rect.y -= self.speed
	def moveDown(self):
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
		self.currentSkinTexture = self.defaultNormal
		self.textureChanged = False
		for x in self.inventory:
			if "slot" in x:
				if self.selectedSlot == x["slot"]:
					if x["item"] == GUN:
						self.currentSkinTexture = self.defaultGunHold
		if mousePressed == "left":
			self.animationTimeIndex += 1
			if self.animationTimeIndex >= len(blockBreakAnimation):
				self.animationTimeIndex = 0
		elif any(value == True for value in pressedKeys.values()):
			self.animationTimeIndex += 1
			if self.animationTimeIndex >= len(walkAnimation):
				self.animationTimeIndex = 0
		else:
			self.animationTimeIndex = 0
		self.angle = math.atan2(mouseY-screen.get_rect().centery, mouseX-screen.get_rect().centerx)
		self.angle = -math.degrees(self.angle)
		if mousePressed == "left":
			self.currentSkinTexture = pygame.transform.rotozoom(blockBreakAnimation[self.animationTimeIndex], self.angle-90, 1)
			for x in self.inventory:
				if "slot" in x:
					if self.selectedSlot == x["slot"]:
						if x["item"] == GUN:
							self.currentSkinTexture = pygame.transform.rotozoom(breakGunAnimation[self.animationTimeIndex], self.angle-90, 1)
			self.textureChanged = True
		elif any(value == True for value in pressedKeys.values()):
			self.currentSkinTexture = pygame.transform.rotozoom(walkAnimation[self.animationTimeIndex], self.angle-90, 1)
			for x in self.inventory:
				if "slot" in x:
					if self.selectedSlot == x["slot"]:
						if x["item"] == GUN:
							self.currentSkinTexture = pygame.transform.rotozoom(walkGunAnimation[self.animationTimeIndex], self.angle-90, 1)
			self.textureChanged = True
		if not self.textureChanged:
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
		self.speed = random.randint(2, 4)
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
	def __init__(self, x, y, text):
		self.text = text
		self.x = x
		self.y = y
		self.textRenderer = fonts[24].render((str(self.text)), config["enableAntialiasing"]["font"], (255, 255, 255))
		self.textRenderer_rect = self.textRenderer.get_rect()

		self.state = "default"
		self.rect = pygame.Rect(self.x, self.y, 256, 64)
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
				text = fonts[24].render(str(self.list[item]), config["enableAntialiasing"]["font"], (255, 255, 255))
				guiSurface.blit(text, (self.x+8, ((self.y+64)+item*64)))
		else:
			guiSurface.blit(dropDownDefault, (self.x, self.y))

class Switch:
	def __init__(self, x, y, state):
		self.rect = switchOn.get_rect(x=x, y=y)
		self.state = state
	def switch(self, var=None):
		self.state = not self.state
	def render(self, screen):
		if self.state:
			screen.blit(switchOn, self.rect)
		else:
			screen.blit(switchOff, self.rect)
class TextInput:
	def __init__(self, x, y, text="", placeholder=""):
		self.text = text
		self.active = False
		self.x = x
		self.y = y
		self.rect = pygame.Rect(x, y, 256, 64)
		self.placeholderText = placeholder
		self.text_surface = fonts[28].render(self.text, config["enableAntialiasing"]["font"], (0, 0, 0))
		self.text_surface_rect = pygame.Rect(x+8, y, self.text_surface.get_width(), self.text_surface.get_height())
		self.text_surface_rect.centery = self.rect.centery
		self.placeholder = fonts[28].render(self.placeholderText, config["enableAntialiasing"]["font"], (179, 179, 179))
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
				self.text_surface = fonts[28].render(self.text, config["enableAntialiasing"]["font"], (0, 0, 0))
				self.text_surface_rect = pygame.Rect(self.x+8, self.y, self.text_surface.get_width(), self.text_surface.get_height()-8)
				self.text_surface_rect.centery = self.rect.centery
				self.placeholder = fonts[28].render(self.placeholderText, config["enableAntialiasing"]["font"], (179, 179, 179))
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

class Spinbox:
	def __init__(self, x, y, w, default, max=None):
		self.x = x
		self.y = y
		self.width = w
		self.value = default
		self.strValue = str(self.value)
		self.max = max
		self.maxText = fonts[24].render(str(self.max), config["enableAntialiasing"]["font"], (3, 252, 111))
		self.value_rect = pygame.Rect(self.x, self.y, self.maxText.get_width(), 64)
		del self.maxText
		self.valueText = fonts[18].render(self.strValue, config["enableAntialiasing"]["font"], (3, 252, 111))
		self.valueText_rect = self.valueText.get_rect(center=self.value_rect.center)
		self.valueTextLine = pygame.Rect(self.valueText_rect.topright[0], self.y+4, 2, 56)
		self.upButton_rect = pygame.Rect(self.value_rect.topright[0], self.y, 32, 32)
		self.downButton_rect = pygame.Rect(self.value_rect.topright[0], self.y+32, 32, 32)
		self.pressed = False
		self.valueEnter = False
		self.timeIndex = 0
		self.speed = 2
	def up(self):
		if self.max != None:
			if self.value < self.max:
				if self.timeIndex < self.speed:
					self.timeIndex += 1
				else:
					pygame.mixer.find_channel().play(spinboxScroll)
					self.timeIndex = 0
					self.value += 1
					self.strValue = str(self.value)
	def down(self):
		if self.value > 0:
			if self.timeIndex < self.speed:
				self.timeIndex += 1
			else:
				pygame.mixer.find_channel().play(spinboxScroll)
				self.timeIndex = 0
				self.value -= 1
				self.strValue = str(self.value)
	def eventHold(self, event):
		if event.type == MOUSEBUTTONDOWN:
			if self.upButton_rect.collidepoint(event.pos):
				self.pressed = True
			elif self.downButton_rect.collidepoint(event.pos):
				self.pressed = True
			if self.value_rect.collidepoint(event.pos):
				self.valueEnter = True
			else:
				self.valueEnter = False
		elif event.type == MOUSEBUTTONUP:
			self.pressed = False
		elif event.type == KEYDOWN:
			if self.valueEnter:
				if event.key == K_BACKSPACE:
					self.strValue = self.strValue[:-1]
					if len(self.strValue) == 0:
						self.strValue = "0"
						self.value = 0
					else:
						self.value = int(self.strValue)
				else:
					if event.key == K_0 or event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4 or event.key == K_5 or event.key == K_6 or event.key == K_7 or event.key == K_8 or event.key == K_9:
						if self.strValue == "0":
							if event.key != K_0:
								self.strValue = event.unicode
								self.value = int(self.strValue)
						else:
							if int(event.unicode + self.strValue) < self.max:
								self.strValue += event.unicode
								self.value = int(self.strValue)
	def render(self, screen):
		if self.pressed:
			if self.upButton_rect.collidepoint(pygame.mouse.get_pos()):
				self.up()
			elif self.downButton_rect.collidepoint(pygame.mouse.get_pos()):
				self.down()
		else:
			self.timeIndex = 0
		self.valueText = fonts[18].render(self.strValue, config["enableAntialiasing"]["font"], (3, 252, 111))
		self.valueText_rect = self.valueText.get_rect(center=self.value_rect.center)
		self.valueTextLine = pygame.Rect(self.valueText_rect.topright[0], self.y+4, 2, 56)
		screen.blit(spinboxUp, self.upButton_rect)
		screen.blit(spinboxDown, self.downButton_rect)
		pygame.draw.rect(screen, (255, 255, 255), self.value_rect, 3, 3)
		screen.blit(self.valueText, self.valueText_rect)
		if self.valueEnter:
			pygame.draw.rect(screen, (255, 255, 255), self.valueTextLine)

class Item:
	def __init__(self, item, x, y):
		self.item = item
		self.x = random.randint(x+16, x+48)-8
		self.y = random.randint(y+16, y+48)-8
		self.angle = random.randint(0,360)
		if self.item == WOODPLANKS:
			self.texture = pygame.transform.scale(woodPlanks, (32, 32)).convert_alpha()
		elif self.item == COBBLESTONE:
			self.texture = pygame.transform.scale(cobblestone, (32, 32)).convert_alpha()
		elif self.item == WOODLOG:
			self.texture = pygame.transform.scale(woodLog, (32, 32)).convert_alpha()
		elif self.item == GUN:
			self.texture = pygame.transform.scale(gunItem, (32, 32)).convert_alpha()
		self.texture = pygame.transform.rotozoom(self.texture, self.angle, 1)
		self.rect = self.texture.get_rect(x=self.x, y=self.y)
	def render(self):
		gameSurface.blit(self.texture, (self.x, self.y))

class InventoryItem:
	def __init__(self, item, amount, slot=None, row=None, col=None, isCraftResult=False):
		self.item = item
		self.slot = slot
		self.row = row
		self.col = col
		self.drag = False
		self.craftSlot = False
		self.amount = amount
		self.isCraftResult = isCraftResult
		self.dropped = False
		self.craftSlotIndex = None
		self.rect = pygame.Rect(0, 0, 160//inventoryScaleIndex, 160//inventoryScaleIndex)
		if slot != None:
			self.rect.x = inventoryRects[64+slot].x
			self.rect.y = inventoryRects[64+slot].y
		elif row != None and col != None:
			self.rect.x = inventoryRects[col+(8*row)].x
			self.rect.y = inventoryRects[col+(8*row)].y
		elif isCraftResult:
			self.rect.x = inventoryGui_rect.x+416//inventoryScaleIndex
			self.rect.y = inventoryGui_rect.y+480//inventoryScaleIndex
		self.previousPos = self.rect.topleft
	def reload(self):
		self.rect = pygame.Rect(0, 0, 160//inventoryScaleIndex, 160//inventoryScaleIndex)
		if self.slot != None:
			self.rect.x = inventoryRects[64+self.slot].x
			self.rect.y = inventoryRects[64+self.slot].y
		elif self.row != None and self.col != None:
			self.rect.x = inventoryRects[self.col+(8*self.row)].x
			self.rect.y = inventoryRects[self.col+(8*self.row)].y
	def eventHandle(self, event):
		if event.type == MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				self.drag = not self.drag
				if not self.drag:
					self.collide = False
					self.craftSlot = False
					for rectIndex in range(len(inventoryRects)):
						if inventoryRects[rectIndex].collidepoint(event.pos):
							self.collide = True
							self.rect.center = inventoryRects[rectIndex].center
							if rectIndex < 64:
								self.slot = None
								self.row = rectIndex//8
								self.col = rectIndex-self.row*8
							else:
								self.row = self.col = None
								if rectIndex > 71:
									self.craftSlot = True
									self.craftSlotIndex = rectIndex-64-8
									if self.craftSlotIndex >= 0:
										if self.item == WOODLOG:
											inventoryItems.append(InventoryItem(WOODPLANKS, self.amount, isCraftResult=True))
								else:
									self.craftSlotIndex = None
									self.slot = rectIndex-64
							break
					if not self.collide:
						self.rect.topleft = self.previousPos
					else:
						self.previousPos = self.rect.topleft
						newInventory = []
						for item in inventoryItems:
							if not item.craftSlot:
								if item.slot != None:
									newInventory.append({
										"item": item.item,
										"amount": item.amount,
										"slot": item.slot
									})
								else:
									newInventory.append({
										"item": item.item,
										"amount": item.amount,
										"col": item.col,
										"row": item.row
									})
						player.inventory = newInventory
				else:
					if self.isCraftResult:
						for x in range(len(inventoryItems)):
							if inventoryItems[x].craftSlotIndex != None:
								if inventoryItems[x].craftSlotIndex >= 0:
									inventoryItems.pop(x)
									break
					else:
						for x in range(len(inventoryItems)):
							if inventoryItems[x].isCraftResult:
								inventoryItems.pop(x)
								

	def render(self):
		amountTitle = fonts[int(64//inventoryScaleIndex)].render(str(self.amount), config["enableAntialiasing"]["font"], (255, 255, 255))
		amountTitle_rect = amountTitle.get_rect(bottomright=(self.rect.bottomright[0],self.rect.bottomright[1]))
		if self.drag:
			self.rect.center = pygame.mouse.get_pos()
		if self.item == WOODPLANKS:
			guiSurface.blit(pygame.transform.scale(woodPlanks, (160//inventoryScaleIndex, 160//inventoryScaleIndex)), self.rect)
		elif self.item == WOODLOG:
			guiSurface.blit(pygame.transform.scale(woodLog, (160//inventoryScaleIndex, 160//inventoryScaleIndex)), self.rect)
		elif self.item == GUN:
			guiSurface.blit(pygame.transform.scale(gunItem, (160//inventoryScaleIndex, 160//inventoryScaleIndex)), self.rect)
		elif self.item == COBBLESTONE:
			guiSurface.blit(pygame.transform.scale(cobblestone, (160//inventoryScaleIndex, 160//inventoryScaleIndex)), self.rect)
		guiSurface.blit(amountTitle, amountTitle_rect)
isLoading = False

def menu():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface

	pygame.display.set_caption("ShootBox - "+translate["mainMenu"])

	versionTitle = fonts[12].render("version: "+version, config["enableAntialiasing"]["font"], (255, 255, 255))
	versionTitle_rect = versionTitle.get_rect(x=4, y=screen.get_height()-versionTitle.get_height())

	play = Button(24, logo.get_height()+16, translate["play"])
	settings = Button(24, play.rect.bottomleft[1], translate["settings"])
	aboutGame = Button(24, settings.rect.bottomleft[1], translate["aboutGame"])
	exit = Button(24, aboutGame.rect.bottomleft[1], translate["exit"])

	logo.set_alpha(0)
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))


		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(logo, (24, 8))

		if logo.get_alpha() < 255:
			logo.set_alpha(logo.get_alpha()+5)

		play.render()
		settings.render()
		aboutGame.render()
		exit.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if play.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						playmodeSelect()
					if settings.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						gameSettings()
					elif aboutGame.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						about()
					if exit.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						pygame.quit()
						sys.exit()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
				versionTitle = fonts[12].render("version: "+version, config["enableAntialiasing"]["font"], (255, 255, 255))
				versionTitle_rect = versionTitle.get_rect(x=4, y=screen.get_height()-versionTitle.get_height())

		guiSurface.blit(versionTitle, versionTitle_rect)

		guiSurface.blit(cursor, pygame.mouse.get_pos())
		
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()
def playmodeSelect():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface
	pygame.display.set_caption("ShootBox - "+translate["modeSelect"])

	singleplayer = Button(24, 80, translate["singleplayer"])
	multiplayer = Button(24, singleplayer.rect.bottomleft[1], translate["multiplayer"])
	back = Button(24, multiplayer.rect.bottomleft[1], translate["back"])

	modeSelectTitle = fonts[36].render(translate["modeSelect"], config["enableAntialiasing"]["font"], (255, 255, 255))

	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(modeSelectTitle, (24, 16))

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
						pygame.mixer.find_channel().play(guiClick)
						singleplayerWorldAction()
					if multiplayer.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						multiplayerAction()
					if back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						menu()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def singleplayerWorldAction():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface
	pygame.display.set_caption("ShootBox - "+translate["modeSelect"])
	load = Button(24, 32, translate["load"])
	create = Button(24, load.rect.bottomleft[1], translate["create"])
	back = Button(24, create.rect.bottomleft[1], translate["back"])
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
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
						pygame.mixer.find_channel().play(guiClick)
						loadWorldMenu()
					if create.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						createWorldMenu()
					if back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						playmodeSelect()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def multiplayerAction():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface
	pygame.display.set_caption("ShootBox - "+translate["modeSelect"])
	title = fonts[36].render(translate["multiplayer"], config["enableAntialiasing"]["font"], (255, 255, 255))
	join = Button(24, 80, translate["join"])
	create = Button(24, join.rect.bottomleft[1], translate["createRoom"])
	back = Button(24, create.rect.bottomleft[1], translate["back"])
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, (24, 24))

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
						pygame.mixer.find_channel().play(guiClick)
						joinMultiplayerMenu()
					if create.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						# serverStartThread = threading.Thread(target=startServer)
						# serverStartThread.setDaemon(True)
						# serverStartThread.start()
						# create.text = "Запуск..."
						pass
					if back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						playmodeSelect()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def startServer():
	# os.system('python "'+os.path.join(serverPath, "server.py")+'"')
	pass

def joinMultiplayerMenu():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface
	title = fonts[36].render(translate["joinServer"], config["enableAntialiasing"]["font"], (255, 255, 255))
	ipInput = TextInput(24, 80, "", placeholder="IP")
	portInput = TextInput(24, ipInput.rect.bottomleft[1], "26675", placeholder=translate["port"])
	join = Button(24, portInput.rect.bottomleft[1], translate["joinServer"])
	back = Button(24, join.rect.bottomleft[1], translate["back"])
	mousePressed = False
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, (24, 24))

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
						pygame.mixer.find_channel().play(guiClick)
						pass
					elif back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						multiplayerAction()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def loadWorldMenu():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface
	worldChoices = []
	for world in range(len(savedWorlds)):
		worldTitle = fonts[24].render(str(savedWorlds[world]["title"]), False, (255, 255, 255))
		worldTitle_rect = worldTitle.get_rect()

		worldJoinButton = pygame.Rect(0, 0, 64, 24)
		worldJoinTitle = fonts[12].render(translate["load"], False, (53, 151, 255))
		worldJoinTitle_rect = worldJoinTitle.get_rect()
		
		worldDeleteButton = pygame.Rect(0, 0, 64, 24)
		worldDeleteTitle = fonts[12].render(translate["delete"], False, (53, 151, 255))
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
	title = fonts[36].render(translate["worldSelect"], config["enableAntialiasing"]["font"], (255, 255, 255))
	notFound = fonts[24].render(translate["noWorlds"], config["enableAntialiasing"]["font"], (255, 255, 255))
	back = Button(24, 160, translate["back"])
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))


		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, (24, 24))

		back.render()

		if len(worldChoices) == 0:
			guiSurface.blit(notFound, (24, 48))

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
							singleplayerGame()
						if worldChoices[x][7].collidepoint(pygame.mouse.get_pos()):
							os.remove(os.path.join(worldsPath, savedWorlds[x]["title"]+".json"))
							del worldChoices[x]
							break
					if back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						singleplayerWorldAction()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
		
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def createWorldMenu():
	last = pygame.time.get_ticks()
	global cubeCooldown, widthInput, heightInput, nameInput, guiSurface
	nameInput = TextInput(24, 80, "", placeholder=translate["worldName"])
	widthInput = TextInput(24, nameInput.rect.bottomleft[1], "", placeholder=translate["width"])
	heightInput = TextInput(24, widthInput.rect.bottomleft[1], "", placeholder=translate["height"])
	pygame.display.set_caption("ShootBox - "+translate["createWorld"])
	title = fonts[36].render(translate["createWorld"], config["enableAntialiasing"]["font"], (255, 255, 255))
	warningTitle = fonts[24].render(" ".join(translate["createWarning"].split()[:6]), config["enableAntialiasing"]["font"], (255, 0, 0))
	warningTitle_rect = warningTitle.get_rect(x=24, y=heightInput.rect.bottomleft[1])
	warningTitle2 = fonts[24].render(" ".join(translate["createWarning"].split()[6:]), config["enableAntialiasing"]["font"], (255, 0, 0))
	warningTitle2_rect = warningTitle2.get_rect(x=24, y=warningTitle_rect.bottomleft[1])
	create = Button(24, warningTitle2_rect.bottomleft[1], translate["create"])
	back = Button(24, create.rect.bottomleft[1]+16, translate["back"])
	mousePressed = False
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, (24, 24))

		nameInput.render()
		widthInput.render()
		heightInput.render()
		guiSurface.blit(warningTitle, warningTitle_rect)
		guiSurface.blit(warningTitle2, warningTitle2_rect)

		create.render()
		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			widthInput.eventHandle(event)
			heightInput.eventHandle(event)
			nameInput.eventHandle(event)
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					mousePressed = True
					if create.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						generateMap()
						singleplayerGame()
					elif back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						singleplayerWorldAction()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def loadMap(world):
	global gameSurface, gameSurface_Rect, player, gameMap
	global mapData
	mapData = world
	gameSurface = pygame.Surface((mapData["size"][0]*64, mapData["size"][1]*64), pygame.HWSURFACE).convert_alpha()
	gameSurface_Rect = gameSurface.get_rect()
	gameSurface_Rect.x, gameSurface_Rect.y = screen.get_rect().center
	gameMap = mapData["map"]
	for block in gameMap:
		if block["block"] == WATER:
			collisionRects.append([pygame.Rect(block["pos"][0]*64, block["pos"][1]*64, 64, 64), False])
		elif block["block"] == TREE:
			collisionRects.append([pygame.Rect(block["pos"][0]*64+24, block["pos"][1]*64+24, 16, 16), True])
		else:
			collisionRects.append([pygame.Rect(block["pos"][0]*64, block["pos"][1]*64, 64, 64), True])
	player = Player(mapData["player"]["pos"][0], mapData["player"]["pos"][1], 0)
	player.inventory = mapData["player"]["inventory"]

def generateMap():
	global gameSurface, gameSurface_Rect, player, mapData
	# chunks = []
	# chunkRects = []
	# for chunkX in range(0, int(widthInput.getInput()), chunkSize*64):
	# 	for chunkY in range(0, int(heightInput.getInput()), chunkSize*64):
	# 		chunkItem = pygame.Surface((chunkSize*64, chunkSize*64))
	# 		chunks.append(chunkItem)
	# 		chunkRects.append(chunkItem.get_rect(x=chunkX, y=chunkY))
	gameSurface = pygame.Surface((int(widthInput.getInput())*64, int(heightInput.getInput())*64), pygame.HWSURFACE).convert_alpha()
	gameSurface_Rect = gameSurface.get_rect()
	gameSurface_Rect.x, gameSurface_Rect.y = screen.get_rect().center
	gameMap.clear()
	for x in range(int(widthInput.text)):
		for y in range(int(heightInput.text)):
			chosenBlock = random.choice(list(generationBlocks))
			if chosenBlock != AIR:
				gameMap.append({"block": chosenBlock, "pos": [x, y]})
				if chosenBlock == TREE:
					collisionRects.append([pygame.Rect(x*64+24, y*64+24, 16, 16), True])
				else:
					collisionRects.append([pygame.Rect(x*64, y*64, 64, 64), True])
	# player = Player(64, 64, 0)
	player = Player(random.randint(0, gameSurface.get_width()), random.randint(0, gameSurface.get_height()), 0)
	mapData = {
		"title": nameInput.text,
		"size": [int(widthInput.text), int(heightInput.text)],
		"player": {
			"pos": [player.x, player.y],
			"inventory": player.inventory
		},
		"map": gameMap
	}
	with open(os.path.join(worldsPath, nameInput.text+".json"), 'w', encoding='utf-8') as f:
		json.dump(mapData, f, ensure_ascii=False, indent=4)

def gameSettings():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface
	pygame.display.set_caption("ShootBox - "+translate["settings"])
	title = fonts[36].render(translate["settings"], config["enableAntialiasing"]["font"], (255, 255, 255))
	graphics = Button(24, 80, translate["graphics"])
	sound = Button(24, graphics.rect.bottomleft[1], translate["sounds"])
	language = Button(24, sound.rect.bottomleft[1], translate["language"])
	back = Button(24, language.rect.bottomleft[1]+16, translate["back"])
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, (24, 24))
		
		graphics.render()
		sound.render()
		language.render()
		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if graphics.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						graphicsSettings()
					elif sound.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						soundSettings()
					elif language.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						languageSettings()
					elif back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						menu()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()

		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def graphicsSettings():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface, screen, guiSurface
	pygame.display.set_caption("ShootBox - "+translate["settings"])
	title = fonts[36].render(translate["graphicsSettings"], config["enableAntialiasing"]["font"], (255, 255, 255))

	fullscreenTitle = fonts[24].render(translate["fullscreenTitle"], config["enableAntialiasing"]["font"], (255, 255, 255))
	fullscreenTitle_rect = fullscreenTitle.get_rect(x=24, y=80)
	fullscreen = Switch(32+fullscreenTitle.get_width(), 80, config["windowFlags"]["fullscreen"])

	gpuAccelerationTitle = fonts[24].render(translate["accelerationTitle"], config["enableAntialiasing"]["font"], (255, 255, 255))
	gpuAccelerationTitle_rect = gpuAccelerationTitle.get_rect(x=24, y=fullscreenTitle_rect.bottomleft[1])
	gpuAcceleration = Switch(32+gpuAccelerationTitle.get_width(), gpuAccelerationTitle_rect.y, config["windowFlags"]["acceleration"])
	
	animationTitle = fonts[24].render(translate["showAnimations"], config["enableAntialiasing"]["font"], (255, 255, 255))
	animationTitle_rect = animationTitle.get_rect(y=gpuAccelerationTitle_rect.bottomleft[1])
	animation = Switch(32+animationTitle.get_width(), animationTitle_rect.y, config["enableAnimations"])

	antialiasTitle = fonts[24].render(translate["useAntialiasing"], True, (255, 255, 255))
	antialiasTitle_rect = antialiasTitle.get_rect(y=animationTitle_rect.bottomleft[1])

	fontAntialiasingTitle = fonts[24].render(translate["fontAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
	fontAntialiasingTitle_rect = fontAntialiasingTitle.get_rect(y=antialiasTitle_rect.bottomleft[1])
	fontAntialiasing = Switch(32+fontAntialiasingTitle.get_width(), fontAntialiasingTitle_rect.y, config["enableAntialiasing"]["font"])

	guiAntialiasingTitle = fonts[24].render(translate["guiAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
	guiAntialiasingTitle_rect = guiAntialiasingTitle.get_rect(y=fontAntialiasingTitle_rect.bottomleft[1])
	guiAntialiasing = Switch(32+guiAntialiasingTitle.get_width(), guiAntialiasingTitle_rect.y, config["enableAntialiasing"]["gui"])

	texturesAntialiasingTitle = fonts[24].render(translate["textureAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
	texturesAntialiasingTitle_rect = texturesAntialiasingTitle.get_rect(y=guiAntialiasingTitle_rect.bottomleft[1])
	texturesAntialiasing = Switch(32+texturesAntialiasingTitle.get_width(), texturesAntialiasingTitle_rect.y, config["enableAntialiasing"]["other"])
	
	showGrassTitle = fonts[24].render(translate["showGrassTexture"], config["enableAntialiasing"]["font"], (255, 255, 255))
	showGrassTitle_rect = showGrassTitle.get_rect(x=24, y=texturesAntialiasingTitle_rect.bottomleft[1])
	showGrass = Switch(32+showGrassTitle.get_width(), showGrassTitle_rect.y, config["showGrass"])

	smartRenderTitle = fonts[24].render(translate["smartRender"], config["enableAntialiasing"]["font"], (255, 255, 255))
	smartRenderTitle_rect = smartRenderTitle.get_rect(x=24, y=showGrassTitle_rect.bottomleft[1])
	smartRender = Switch(32+smartRenderTitle.get_width(), smartRenderTitle_rect.y, config["smartRender"])

	renderDistanceTitle = fonts[24].render(translate["renderDistance"], config["enableAntialiasing"]["font"], (255, 255, 255))
	renderDistanceTitle_rect = renderDistanceTitle.get_rect(x=24, y=smartRenderTitle_rect.bottomleft[1])
	renderDistance = Spinbox(32+renderDistanceTitle.get_width(), renderDistanceTitle_rect.y, 128, config["renderDistance"], 80)

	back = Button(24, screen.get_height()-72, translate["back"])
	apply = Button(back.rect.bottomright[0], screen.get_height()-72, translate["apply"])
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, (24, 24))

		guiSurface.blit(fullscreenTitle, fullscreenTitle_rect)
		guiSurface.blit(gpuAccelerationTitle, gpuAccelerationTitle_rect)
		guiSurface.blit(animationTitle, (24, animationTitle_rect.y))
		guiSurface.blit(antialiasTitle, (24, animationTitle_rect.bottomleft[1]))
		guiSurface.blit(fontAntialiasingTitle, (24, antialiasTitle_rect.bottomleft[1]))
		guiSurface.blit(guiAntialiasingTitle, (24, fontAntialiasingTitle_rect.bottomleft[1]))
		guiSurface.blit(texturesAntialiasingTitle, (24, guiAntialiasingTitle_rect.bottomleft[1]))
		guiSurface.blit(showGrassTitle, showGrassTitle_rect)
		guiSurface.blit(smartRenderTitle, smartRenderTitle_rect)
		guiSurface.blit(renderDistanceTitle, renderDistanceTitle_rect)

		fullscreen.render(guiSurface)
		gpuAcceleration.render(guiSurface)
		animation.render(guiSurface)
		fontAntialiasing.render(guiSurface)
		guiAntialiasing.render(guiSurface)
		texturesAntialiasing.render(guiSurface)
		showGrass.render(guiSurface)
		smartRender.render(guiSurface)
		renderDistance.render(guiSurface)
		apply.render()
		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			renderDistance.eventHold(event)
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if fullscreen.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						fullscreen.switch()
						config["windowFlags"]["fullscreen"] = not config["windowFlags"]["fullscreen"]
					elif gpuAcceleration.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						gpuAcceleration.switch()
						config["windowFlags"]["acceleration"] = not config["windowFlags"]["acceleration"]
					elif animation.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						animation.switch()
						config["enableAnimations"] = not config["enableAnimations"]
					elif fontAntialiasing.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						fontAntialiasing.switch()
						config["enableAntialiasing"]["font"] = not config["enableAntialiasing"]["font"]
					elif guiAntialiasing.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						guiAntialiasing.switch()
						config["enableAntialiasing"]["gui"] = not config["enableAntialiasing"]["gui"]
					elif texturesAntialiasing.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						texturesAntialiasing.switch()
						config["enableAntialiasing"]["other"] = not config["enableAntialiasing"]["other"]
					elif showGrass.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						showGrass.switch()
						config["showGrass"] = not config["showGrass"]
					elif smartRender.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiSwitch)
						smartRender.switch()
						config["smartRender"] = not config["smartRender"]
					elif apply.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						windowSize = ()
						if config["windowFlags"]["fullscreen"]:
							windowFlags = pygame.FULLSCREEN
						else:
							windowFlags = pygame.RESIZABLE
							# windowSize = (config["resolution"][0], config["resolution"][1])
							windowSize = (1024, 576)
						if config["windowFlags"]["acceleration"]:
							windowFlags = windowFlags | pygame.HWSURFACE | pygame.DOUBLEBUF
						pygame.display.quit()
						pygame.display.init()
						displayInfo = pygame.display.Info()
						if config["windowFlags"]["fullscreen"]:
							windowSize = (displayInfo.current_w, displayInfo.current_h)
						screen = pygame.display.set_mode(windowSize, windowFlags)
						pygame.mouse.set_visible(False)
						guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
						guiSurface.convert_alpha()
						title = fonts[36].render(translate["graphicsSettings"], config["enableAntialiasing"]["font"], (255, 255, 255))
						fullscreenTitle = fonts[24].render(translate["fullscreenTitle"], config["enableAntialiasing"]["font"], (255, 255, 255))
						animationTitle = fonts[24].render(translate["showAnimations"], config["enableAntialiasing"]["font"], (255, 255, 255))
						antialiasTitle = fonts[24].render(translate["useAntialiasing"], True, (255, 255, 255))
						fontAntialiasingTitle = fonts[24].render(translate["fontAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
						guiAntialiasingTitle = fonts[24].render(translate["guiAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
						texturesAntialiasingTitle = fonts[24].render(translate["textureAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
						texturesAntialiasing = Switch(32+texturesAntialiasingTitle.get_width(), texturesAntialiasingTitle_rect.y, config["enableAntialiasing"]["other"])
						reloadTextures(config["enableAntialiasing"]["gui"], config["enableAntialiasing"]["other"])

						fullscreen = Switch(32+fullscreenTitle.get_width(), 80, config["windowFlags"]["fullscreen"])
						animation = Switch(32+animationTitle.get_width(), animationTitle_rect.y, config["enableAnimations"])
						fontAntialiasing = Switch(32+fontAntialiasingTitle.get_width(), fontAntialiasingTitle_rect.y, config["enableAntialiasing"]["font"])
						guiAntialiasing = Switch(32+guiAntialiasingTitle.get_width(), guiAntialiasingTitle_rect.y, config["enableAntialiasing"]["gui"])
						texturesAntialiasing = Switch(32+texturesAntialiasingTitle.get_width(), texturesAntialiasingTitle_rect.y, config["enableAntialiasing"]["other"])
						back = Button(24, screen.get_height()-72, translate["back"])
						apply = Button(back.rect.bottomright[0], screen.get_height()-72, translate["apply"])
						config["renderDistance"] = renderDistance.value
						with open('config.json', 'w', encoding='utf-8') as f:
							json.dump(config, f, ensure_ascii=False, indent=4)
					elif back.rect.collidepoint(event.pos):
						pygame.mixer.find_channel().play(guiClick)
						gameSettings()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()
					

		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def soundSettings():
	last = pygame.time.get_ticks()
	global cubeCooldown, translate, guiSurface
	pygame.display.set_caption("ShootBox - "+translate["soundSettings"])
	title = fonts[36].render(translate["soundSettings"], config["enableAntialiasing"]["font"], (255, 255, 255))
	sfxTitle = fonts[24].render(translate["sfx"], config["enableAntialiasing"]["font"], (255, 255, 255))
	sfxTitle_rect = sfxTitle.get_rect(x=24, y=80)
	sfx = Spinbox(sfxTitle_rect.topright[0], sfxTitle_rect.topright[1], 128, config["sfx"], 100)
	musicTitle = fonts[24].render(translate["music"], config["enableAntialiasing"]["font"], (255, 255, 255))
	musicTitle_rect = musicTitle.get_rect(x=24, y=sfx.value_rect.bottomleft[1])
	music = Spinbox(musicTitle_rect.topright[0], musicTitle_rect.topright[1], 128, config["music"], 100)
	back = Button(24, screen.get_height()-72, translate["back"])
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		mouseRel = pygame.mouse.get_rel()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			sfx.eventHold(event)
			music.eventHold(event)
			# music.eventHandle(event)
			if event.type == MOUSEBUTTONDOWN:
				if back.rect.collidepoint(event.pos):
					pygame.mixer.find_channel().play(guiClick)
					gameSettings()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()

		guiSurface.blit(title, (24, 24))

		guiSurface.blit(sfxTitle, sfxTitle_rect)
		guiSurface.blit(musicTitle, musicTitle_rect)
		music.render(guiSurface)
		sfx.render(guiSurface)
		back.render()
		config["sfx"] = sfx.value
		config["music"] = music.value
		with open('config.json', 'w', encoding='utf-8') as f:
			json.dump(config, f, ensure_ascii=False, indent=4)
		for channel in range(pygame.mixer.get_num_channels()):
			pygame.mixer.Channel(channel).set_volume(config["sfx"]/100)
		pygame.mixer.music.set_volume(config['music']/100)
		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()


def languageSettings():
	last = pygame.time.get_ticks()
	global cubeCooldown, translate, guiSurface
	pygame.display.set_caption("ShootBox - "+translate["languageSelect"])
	title = fonts[36].render(translate["languageSelect"], config["enableAntialiasing"]["font"], (255, 255, 255))
	if config["lang"] == "en":
		english = fonts[24].render("English", config["enableAntialiasing"]["font"], (255, 255, 255))
	else:
		english = fonts[24].render("English", config["enableAntialiasing"]["font"], (180, 180, 180))
	if config["lang"] == "ru":
		russian = fonts[24].render("Русский", config["enableAntialiasing"]["font"], (255, 255, 255))
	else:
		russian = fonts[24].render("Русский", config["enableAntialiasing"]["font"], (180, 180, 180))
	english_rect = english.get_rect(x=24, y=80)
	russian_rect = russian.get_rect(x=24, y=english_rect.bottomleft[1])
	back = Button(24, screen.get_height()-72, translate["back"])
	apply = Button(back.rect.bottomright[0], screen.get_height()-72, translate["apply"])
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, (24, 24))

		guiSurface.blit(english, english_rect)
		guiSurface.blit(russian, russian_rect)

		apply.render()
		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				if english_rect.collidepoint(event.pos):
					english = fonts[24].render("English", config["enableAntialiasing"]["font"], (255, 255, 255))
					russian = fonts[24].render("Русский", config["enableAntialiasing"]["font"], (180, 180, 180))
					config["lang"] = "en"
				elif russian_rect.collidepoint(event.pos):
					english = fonts[24].render("English", config["enableAntialiasing"]["font"], (180, 180, 180))
					russian = fonts[24].render("Русский", config["enableAntialiasing"]["font"], (255, 255, 255))
					config["lang"] = "ru"
				elif apply.rect.collidepoint(event.pos):
					pygame.mixer.find_channel().play(guiClick)
					with open('config.json', 'w', encoding='utf-8') as f:
						json.dump(config, f, ensure_ascii=False, indent=4)
					if config["lang"] == "en":
						with open(os.path.join(langPath, "en.json"), encoding='utf-8') as f:
							translate = json.load(f)
					elif config["lang"] == "ru":
						with open(os.path.join(langPath, "ru.json"), encoding='utf-8') as f:
							translate = json.load(f)
					pygame.display.set_caption("ShootBox - "+translate["settings"])
					title = fonts[36].render(translate["languageSelect"], config["enableAntialiasing"]["font"], (255, 255, 255))
					apply = Button(280, screen.get_height()-72, translate["apply"])
					back = Button(24, screen.get_height()-72, translate["back"])
				elif back.rect.collidepoint(event.pos):
					pygame.mixer.find_channel().play(guiClick)
					gameSettings()
			if event.type == VIDEORESIZE:
				guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
				guiSurface.convert_alpha()

		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()

def about():
	last = pygame.time.get_ticks()
	global cubeCooldown, guiSurface
	title = fonts[36].render(translate["aboutGame"], config["enableAntialiasing"]["font"], (255, 255, 255))
	title_rect = title.get_rect(x=24, y=24)
	testers = ["The TLS"]
	back = Button(24, screen.get_height()-72, translate["back"])
	logo.set_alpha(255)
	logo_rect = logo.get_rect(x=24, y=title_rect.bottomleft[1])
	testersTitle = fonts[28].render(translate["testersTitle"], config["enableAntialiasing"]["font"], (255, 255, 255))
	testersTitle_rect = testersTitle.get_rect(x=24, y=logo_rect.bottomleft[1])
	discord.set_alpha(155)
	github.set_alpha(155)
	while 1:
		clock.tick(60)
		screen.fill((28, 21, 53))
		guiSurface.fill((28, 21, 53))

		now = pygame.time.get_ticks()
		if now - last >= cubeCooldown:
			last = now
			if len(summonedCubes) < 12:
				summonedCubes.append(Cube())
				cubeCooldown = random.randint(350, 600)
		
		i = 0
		while i <= len(summonedCubes):
			try:
				summonedCubes[i].render()
				if summonedCubes[i].rect.y < -128:
					summonedCubes.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1

		guiSurface.blit(title, title_rect)

		guiSurface.blit(logo, logo_rect)

		guiSurface.blit(testersTitle, testersTitle_rect)

		for nameIndex in range(len(testers)):
			testerName = fonts[20].render(testers[nameIndex], config["enableAntialiasing"]["font"], (255, 255, 255))
			guiSurface.blit(testerName, (24, testersTitle_rect.bottomleft[1]+nameIndex*testerName.get_height()))

		discord_rect = discord.get_rect(x=24, y=testersTitle_rect.bottomleft[1]+nameIndex*testerName.get_height()+32)
		guiSurface.blit(discord, discord_rect)
		github_rect = github.get_rect(x=discord_rect.topright[0]+8, y=discord_rect.y)
		guiSurface.blit(github, github_rect)

		back.render()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				if back.rect.collidepoint(event.pos):
					menu()
				if discord_rect.collidepoint(event.pos):
					webbrowser.open_new_tab("https://discord.gg/vbRw7CMC4j")
				elif github_rect.collidepoint(event.pos):
					webbrowser.open_new_tab("https://github.com/f1refa11/shootbox")

		if discord_rect.collidepoint(pygame.mouse.get_pos()):
			if discord.get_alpha() < 255:
				discord.set_alpha(discord.get_alpha()+4)
		else:
			if discord.get_alpha() > 155:
				discord.set_alpha(discord.get_alpha()-4)
		
		if github_rect.collidepoint(pygame.mouse.get_pos()):
			if github.get_alpha() < 255:
				github.set_alpha(github.get_alpha()+4)
		else:
			if github.get_alpha() > 155:
				github.set_alpha(github.get_alpha()-4)

		guiSurface.blit(cursor, pygame.mouse.get_pos())
			
		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))

		screen.blit(guiSurface, (0,0))

		pygame.display.update()


def singleplayerGame():
	pygame.display.set_caption("ShootBox - Playing Singleplayer")
	pygame.mixer.music.stop()
	pygame.mixer.music.unload()
	global screen, guiSurface, gameSurface, gameSurface_Rect, paused, inventoryGuiOpened, blockDestroyTime, inventoryGui, inventoryGui_rect, inventoryScaleIndex, mousePressed, pauseMenu, collisionRects, mapData, blocksOffsetX, blocksOffsetY
	paused = None
	inventoryGuiOpened = False
	blocksOffsetX = 0
	blocksOffsetY = 0
	last = pygame.time.get_ticks()
	last1 = pygame.time.get_ticks()
	last2 = pygame.time.get_ticks()
	last3 = pygame.time.get_ticks()
	resume = Button(32, 40, translate["continueGame"])
	settings = Button(32, resume.rect.bottomleft[1], translate["settings"])
	exit = Button(32, settings.rect.bottomleft[1], translate["exit"])
	fullscreenTitle = fonts[24].render(translate["fullscreenTitle"], config["enableAntialiasing"]["font"], (255, 255, 255))
	fullscreenTitle_rect = fullscreenTitle.get_rect(x=24, y=40)
	gpuAccelerationTitle = fonts[24].render(translate["accelerationTitle"], config["enableAntialiasing"]["font"], (255, 255, 255))
	gpuAccelerationTitle_rect = gpuAccelerationTitle.get_rect(x=24, y=fullscreenTitle_rect.bottomleft[1])
	showAnimationsTitle = fonts[24].render(translate["showAnimations"], config["enableAntialiasing"]["font"], (255, 255, 255))
	showAnimationsTitle_rect = showAnimationsTitle.get_rect(x=24, y=gpuAccelerationTitle_rect.bottomleft[1])
	antialiasTitle = fonts[24].render(translate["useAntialiasing"], config["enableAntialiasing"]["font"], (255, 255, 255))
	antialiasTitle_rect = antialiasTitle.get_rect(x=24, y=showAnimationsTitle_rect.bottomleft[1])
	fontAntialiasTitle = fonts[24].render(translate["fontAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
	fontAntialiasTitle_rect = fontAntialiasTitle.get_rect(x=24, y=antialiasTitle_rect.bottomleft[1])
	guiAntialiasTitle = fonts[24].render(translate["guiAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
	guiAntialiasTitle_rect = guiAntialiasTitle.get_rect(x=24, y=fontAntialiasTitle_rect.bottomleft[1])
	textureAntialiasTitle = fonts[24].render(translate["textureAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
	textureAntialiasTitle_rect = textureAntialiasTitle.get_rect(x=24, y=guiAntialiasTitle_rect.bottomleft[1])
	fullscreen = Switch(32+fullscreenTitle.get_width(), fullscreenTitle_rect.y, config["windowFlags"]["fullscreen"])
	gpuAcceleration = Switch(32+gpuAccelerationTitle.get_width(), gpuAccelerationTitle_rect.y, config["windowFlags"]["acceleration"])
	showAnimations = Switch(32+showAnimationsTitle.get_width(), showAnimationsTitle_rect.y, config["enableAnimations"])
	fontAntialias = Switch(32+fontAntialiasTitle.get_width(), fontAntialiasTitle_rect.y, config["enableAntialiasing"]["font"])
	guiAntialias = Switch(32+guiAntialiasTitle.get_width(), guiAntialiasTitle_rect.y, config["enableAntialiasing"]["gui"])
	textureAntialias = Switch(32+textureAntialiasTitle.get_width(), textureAntialiasTitle_rect.y, config["enableAntialiasing"]["other"])
	back = Button(24, pauseMenu.get_width()-16, translate["back"])
	apply = Button(24, back.rect.y-64, translate["apply"])
	animationFrame = 0
	mousePressed = False
	inventoryRects.clear()
	for row in range(9):
		for col in range(8):
			inventoryRects.append(pygame.Rect(inventoryGui_rect.x+(896+(176*col))//inventoryScaleIndex, inventoryGui_rect.y+(240+(176*row))//inventoryScaleIndex, 160//inventoryScaleIndex, 160//inventoryScaleIndex))
	for craftSlot in range(3):
		inventoryRects.append(pygame.Rect(inventoryGui_rect.x+(224+(192*craftSlot))//inventoryScaleIndex, inventoryGui_rect.y+(224//inventoryScaleIndex), 160//inventoryScaleIndex, 160//inventoryScaleIndex))
	inventoryRects.append(pygame.Rect(inventoryGui_rect.x+416//inventoryScaleIndex, inventoryGui_rect.y+480//inventoryScaleIndex, 160//inventoryScaleIndex, 160//inventoryScaleIndex))
	inventoryItems.clear()
	for item in player.inventory:
		if "slot" in item:
			inventoryItems.append(InventoryItem(item["item"], item["amount"], slot=item["slot"]))
		else:
			inventoryItems.append(InventoryItem(item["item"], item["amount"], row=item["row"], col=item["col"]))
	if config["smartRender"]:
		renderRect = pygame.Rect(player.rect.centerx-screen.get_width()//2, player.rect.centery-screen.get_height()//2, screen.get_width(), screen.get_height())
	else:
		renderRect = pygame.Rect(player.rect.centerx-config["renderDistance"]*32, player.rect.centery-config["renderDistance"]*32, config["renderDistance"]*64, config["renderDistance"]*64)
	while 1:
		sameBlock = False
		clock.tick(60)
		screen.fill((42, 170, 255))
		gameSurface.fill((29, 189, 104))
		guiSurface.fill((0,0,0,0))
		
		
		oldScreen = [screen.get_width(), screen.get_height()]

		now1 = pygame.time.get_ticks()
		if now1 - last1 >= 50:
			last1 = now1
			if animationFrame != 29:
				animationFrame += 1
			else:
				animationFrame = 0
		

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if paused == None and inventoryGuiOpened == False:
					if event.key == K_w:
						pressedKeys["up"] = True
					elif event.key == K_s:
						pressedKeys["down"] = True
					elif event.key == K_a:
						pressedKeys["left"] = True
					elif event.key == K_d:
						pressedKeys["right"] = True
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
				if event.key == K_e:
					if paused != None:
						paused = None
					else:
						inventoryGuiOpened = not inventoryGuiOpened
				elif event.key == K_ESCAPE:
					if inventoryGuiOpened:
						inventoryGuiOpened = False
					else:
						if paused == None:
							paused = "main"
						elif paused != None:
							paused = None
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
					if paused == "main":
						if resume.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiClick)
							paused = None
						elif settings.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiClick)
							paused = "settings"
						elif exit.rect.collidepoint(event.pos):
							mapData["player"]["pos"] = [player.x, player.y]
							mapData["map"] = gameMap
							with open(os.path.join(worldsPath, mapData["title"]+".json"), 'w', encoding='utf-8') as f:
								json.dump(mapData, f, ensure_ascii=False, indent=4)
							collisionRects = []
							mapData = {}
							pygame.mixer.find_channel().play(guiClick)
							menu()
					elif paused == "settings":
						if fullscreen.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiSwitch)
							fullscreen.switch()
							config["windowFlags"]["fullscreen"] = not config["windowFlags"]["fullscreen"]
						elif gpuAcceleration.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiSwitch)
							gpuAcceleration.switch()
							config["windowFlags"]["acceleration"] = not config["windowFlags"]["acceleration"]
						elif showAnimations.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiSwitch)
							showAnimations.switch()
							config["enableAnimations"] = not config["enableAnimations"]
						elif fontAntialias.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiSwitch)
							fontAntialias.switch()
							config["enableAntialiasing"]["font"] = not config["enableAntialiasing"]["font"]
						elif guiAntialias.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiSwitch)
							guiAntialias.switch()
							config["enableAntialiasing"]["gui"] = not config["enableAntialiasing"]["gui"]
						elif textureAntialias.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiSwitch)
							textureAntialias.switch()
							config["enableAntialiasing"]["other"] = not config["enableAntialiasing"]["other"]
						elif back.rect.collidepoint(event.pos):
							paused = "main"
						elif apply.rect.collidepoint(event.pos):
							pygame.mixer.find_channel().play(guiClick)
							fullscreenTitle = fonts[24].render(translate["fullscreenTitle"], config["enableAntialiasing"]["font"], (255, 255, 255))
							showAnimationsTitle = fonts[24].render(translate["showAnimations"], config["enableAntialiasing"]["font"], (255, 255, 255))
							antialiasTitle = fonts[24].render(translate["useAntialiasing"], config["enableAntialiasing"]["font"], (255, 255, 255))
							fontAntialiasTitle = fonts[24].render(translate["fontAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
							guiAntialiasTitle = fonts[24].render(translate["guiAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
							textureAntialiasTitle = fonts[24].render(translate["textureAntialias"], config["enableAntialiasing"]["font"], (255, 255, 255))
							windowSize = ()
							displayInfo = pygame.display.Info()
							if config["windowFlags"]["fullscreen"]:
								windowFlags = pygame.FULLSCREEN
								windowSize = (displayInfo.current_w, displayInfo.current_h)
							else:
								windowFlags = pygame.RESIZABLE
								windowSize = (config["resolution"][0], config["resolution"][1])
							if config["windowFlags"]["acceleration"]:
								windowFlags = windowFlags | pygame.HWSURFACE | pygame.DOUBLEBUF
							screen = pygame.display.set_mode(windowSize, windowFlags)
							guiSurface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
							guiSurface.convert_alpha()
							reloadTextures(config["enableAntialiasing"]["gui"], config["enableAntialiasing"]["other"])
							player.defaultNormal = pygame.image.load(os.path.join(playerTexturesPath, "idle.png"))
							player.defaultGunHold = pygame.image.load(os.path.join(playerTexturesPath, "gunHold.png"))
							if config["enableAntialiasing"]["other"]:
								player.defaultNormal = pygame.transform.smoothscale(player.defaultNormal, (64, 64)).convert_alpha()
								player.defaultGunHold = pygame.transform.smoothscale(player.defaultGunHold, (64, 64)).convert_alpha()
							else:
								player.defaultNormal = pygame.transform.scale(player.defaultNormal, (64, 64)).convert_alpha()
								player.defaultGunHold = pygame.transform.scale(player.defaultGunHold, (64, 64)).convert_alpha()
							inventoryGui_rect = inventoryGui.get_rect()
							inventoryGui_rect.center = screen.get_rect().center
							fullscreen = Switch(32+fullscreenTitle.get_width(), fullscreenTitle_rect.y, config["windowFlags"]["fullscreen"])
							showAnimations = Switch(32+showAnimationsTitle.get_width(), showAnimationsTitle_rect.y, config["enableAnimations"])
							fontAntialias = Switch(32+fontAntialiasTitle.get_width(), fontAntialiasTitle_rect.y, config["enableAntialiasing"]["font"])
							guiAntialias = Switch(32+guiAntialiasTitle.get_width(), guiAntialiasTitle_rect.y, config["enableAntialiasing"]["gui"])
							textureAntialias = Switch(32+textureAntialiasTitle.get_width(), textureAntialiasTitle_rect.y, config["enableAntialiasing"]["other"])
							back = Button(24, pauseMenu.get_width()-16, translate["back"])
							apply = Button(24, back.rect.y-64, translate["apply"])
							with open('config.json', 'w', encoding='utf-8') as f:
								json.dump(config, f, ensure_ascii=False, indent=4)
					else:
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
				inventoryScaleIndex = inventoryGui_source.get_height() / (screen.get_height()-8)
				inventoryGui = pygame.transform.smoothscale(inventoryGui_source, (inventoryGui_source.get_width()/inventoryScaleIndex, screen.get_height()-8)).convert_alpha()
				inventoryGui_rect = inventoryGui.get_rect()
				inventoryGui_rect.center = screen.get_rect().center
				if config["enableAntialiasing"]["gui"]:
					method = getattr(pygame.transform, "smoothscale")
				else:
					method = getattr(pygame.transform, "scale")
				global inventoryCell, inventoryCell_green, inventoryHotbar
				inventoryCell = method(inventoryGui_cell_source, (160//inventoryScaleIndex, 160//inventoryScaleIndex))
				inventoryCell_green = method(inventoryGui_greenCell_source, (160//inventoryScaleIndex, 160//inventoryScaleIndex))
				inventoryHotbar = method(inventoryGui_hotbar_source, (160//inventoryScaleIndex, 160//inventoryScaleIndex))
				inventoryRects.clear()
				for row in range(9):
					for col in range(8):
						inventoryRects.append(pygame.Rect(inventoryGui_rect.x+(896+(176*col))//inventoryScaleIndex, inventoryGui_rect.y+(240+(176*row))//inventoryScaleIndex, 160//inventoryScaleIndex, 160//inventoryScaleIndex))
				for craftSlot in range(3):
					inventoryRects.append(pygame.Rect(inventoryGui_rect.x+(224+(192*craftSlot))//inventoryScaleIndex, inventoryGui_rect.y+(224//inventoryScaleIndex), 160//inventoryScaleIndex, 160//inventoryScaleIndex))
				inventoryRects.append(pygame.Rect(inventoryGui_rect.x+416//inventoryScaleIndex, inventoryGui_rect.y+480//inventoryScaleIndex, 160//inventoryScaleIndex, 160//inventoryScaleIndex))
				for item in inventoryItems:
					item.reload()
			if inventoryGuiOpened:
				for item in inventoryItems:
					item.eventHandle(event)
		

		if mousePressed == "right":
			for playerSlot in player.inventory:
				if "slot" in playerSlot:
					if player.selectedSlot == playerSlot["slot"]:
						if playerSlot["item"] == GUN:
							pass
						elif playerSlot["item"] == WOODPLANKS:
							if playerSlot["amount"] != 0:
								if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
									sameBlock = False
									for block in gameMap:
										sameBlock = False
										if block["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
											sameBlock = True
											break
									
									if not sameBlock:
										collisionRects.append([pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), True])
										gameMap.append({"block": WOODPLANKS, "pos": [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]})
										playerSlot["amount"] -= 1
									if player.rect.colliderect(collisionRects[-1][0]):
										collisionRects.remove([pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), True])
										gameMap.pop(-1)
										playerSlot["amount"] += 1
						elif playerSlot["item"] == COBBLESTONE:
							if playerSlot["amount"] != 0:
								if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
									sameBlock = False
									for block in gameMap:
										sameBlock = False
										if block["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
											sameBlock = True
											break
									
									if not sameBlock:
										collisionRects.append([pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), True])
										gameMap.append({"block": COBBLESTONE, "pos": [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]})
										playerSlot["amount"] -= 1
									if player.rect.colliderect(collisionRects[-1][0]):
										collisionRects.remove([pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), True])
										gameMap.pop(-1)
										playerSlot["amount"] += 1
		elif mousePressed == "left":
			now2 = pygame.time.get_ticks()
			if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
				i = 0
				while i <= len(gameMap):
					try:
						if gameMap[i]["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
							if gameMap[i]["block"] != WATER:
								if now2 - last2 >= 250:
									last2 = now2
									if blockDestroyTime < 11:
										blockDestroyTime += 1
								if blockDestroyTime >= 11:
									if gameMap[i]["block"] == WOODPLANKS:
										itemsList.append(Item(WOODPLANKS, gameMap[i]["pos"][0]*64, gameMap[i]["pos"][1]*64))
										collisionRects.remove([pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), True])
									elif gameMap[i]["block"] == COBBLESTONE:
										itemsList.append(Item(COBBLESTONE, gameMap[i]["pos"][0]*64, gameMap[i]["pos"][1]*64))
										collisionRects.remove([pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), True])
									elif gameMap[i]["block"] == TREE:
										for x in range(random.randint(2,4)):
											itemsList.append(Item(WOODLOG, gameMap[i]["pos"][0]*64, gameMap[i]["pos"][1]*64))
										collisionRects.remove([pygame.Rect((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64+24, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64+24, 16, 16), True])
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

		if any(value == True for value in pressedKeys.values()):
			now3 = pygame.time.get_ticks()
			if now3 - last3 >= 250:
				last3 = now3
				pygame.mixer.find_channel().play(footstepGrass)

		if config["showGrass"]:
			for x in range(0,gameSurface.get_width(), 64):
				for y in range(0,gameSurface.get_height(), 64):
					if renderRect.collidepoint(x,y):
						gameSurface.blit(grass, (x,y))


		i = 0
		while i <= len(shotBullets):
			try:
				shotBullets[i].render()
				if not gameSurface.get_rect().colliderect(shotBullets[i].rect):
					shotBullets.pop(i)
					i -= 1
			except IndexError:
				pass
			i += 1


		z = 0
		while z <= len(itemsList):
			try:
				itemsList[z].render()
				if player.rect.colliderect(itemsList[z].rect):
					breakLoop = True
					if any(item == itemsList[z].item for item in COLLECTABLE_ITEMS):
						for item in player.inventory:
							if item["item"] == itemsList[z].item:
								item["amount"] += 1
								breakLoop = False
								inventoryItems.clear()
								for item in player.inventory:
									if "slot" in item:
										inventoryItems.append(InventoryItem(item["item"], item["amount"], slot=item["slot"]))
									else:
										inventoryItems.append(InventoryItem(item["item"], item["amount"], row=item["row"], col=item["col"]))
								break
						if breakLoop:
							nextSlot = 0
							for i in range(8):
								slotIsBusy = False
								for y in player.inventory:
									if "slot" in y:
										if y["slot"] == i:
											slotIsBusy = True
											break
								if not slotIsBusy:
									nextSlot = i
									break
							player.inventory.append({"item": itemsList[z].item, "amount": 1, "slot": nextSlot})
							inventoryItems.append(InventoryItem(itemsList[z].item, 1, slot=nextSlot))
					itemsList.pop(z)
					z -= 1
			except IndexError:
				pass
			z += 1

		for b in gameMap:
			if renderRect.collidepoint(b["pos"][0]*64, b["pos"][1]*64):
				if b["block"] == TREE:
					gameSurface.blit(tree, (b["pos"][0]*64, b["pos"][1]*64))
				elif b["block"] == WOODPLANKS:
					gameSurface.blit(woodPlanks, (b["pos"][0]*64, b["pos"][1]*64))
				elif b["block"] == COBBLESTONE:
					gameSurface.blit(cobblestone, (b["pos"][0]*64, b["pos"][1]*64))
				elif b["block"] == WATER:
					gameSurface.blit(water[animationFrame], (b["pos"][0]*64, b["pos"][1]*64))
				elif b["block"] == SAND:
					gameSurface.blit(sand, (b["pos"][0]*64, b["pos"][1]*64))

				if mousePressed == "left":
					if b["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
						if blockDestroyTime != 0:
							gameSurface.blit(destroyBlock[blockDestroyTime], (b["pos"][0]*64, b["pos"][1]*64))
		if int(math.hypot(screen.get_rect().centerx-pygame.mouse.get_pos()[0], screen.get_rect().centery-pygame.mouse.get_pos()[1])) <= 64*3:
					if not config["highlightSurface"]:
						if gameMap[b]["pos"] == [(pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64]:
							pygame.draw.rect(gameSurface, (255, 255, 255), (gameMap[b]["pos"][0]*64, gameMap[b]["pos"][1]*64, 64, 64), 3)
					else:
						pygame.draw.rect(gameSurface, (255, 255, 255), ((pygame.mouse.get_pos()[0]-gameSurface_Rect.x)//64*64, (pygame.mouse.get_pos()[1]-gameSurface_Rect.y)//64*64, 64, 64), 2)
		player.render()

		# s = 0
		# c = 0
		# if len(collisionRects) > 0:
		# 	if len(shotBullets) > 0:
		# 		while c <= len(collisionRects):
		# 			while s < len(shotBullets):
		# 				if collisionRects[c][0].colliderect(shotBullets[s].rect):
		# 					shotBullets.remove(shotBullets[s])
		# 					s -= 1
		# 				s += 1
		# 			c += 1

		for h in range(8):
			guiSurface.blit(hotBar, (guiSurface.get_width()//2-256+h*64, guiSurface.get_height()-64))
		for x in player.inventory:
			if x["item"] == GUN:
				if "slot" in x:
					guiSurface.blit(gunItem, (guiSurface.get_width()//2-256+x["slot"]*64, guiSurface.get_height()-64))
					text = fonts[16].render(str(x["amount"]), config["enableAntialiasing"]["font"], (255, 255, 255))
					guiSurface.blit(text, (guiSurface.get_width()//2-256+x["slot"]*64+32, guiSurface.get_height()-64+32))
			elif x["item"] == WOODPLANKS:
				if x["amount"] != 0:
					if "slot" in x:
						guiSurface.blit(woodPlanks_item, (guiSurface.get_width()//2-256+x["slot"]*64+8, guiSurface.get_height()-64+8))
						text = fonts[16].render(str(x["amount"]), config["enableAntialiasing"]["font"], (255, 255,255))
						guiSurface.blit(text, (guiSurface.get_width()//2-256+x["slot"]*64+32, guiSurface.get_height()-64+32))
			elif x["item"] == WOODLOG:
				if "slot" in x:
					guiSurface.blit(woodLog_item, (guiSurface.get_width()//2-256+x["slot"]*64+8, guiSurface.get_height()-64+8))
					text = fonts[16].render(str(x["amount"]), config["enableAntialiasing"]["font"], (255, 255,255))
					guiSurface.blit(text, (guiSurface.get_width()//2-256+x["slot"]*64+32, guiSurface.get_height()-64+32))
			elif x["item"] == COBBLESTONE:
				if x["amount"] != 0:
					if "slot" in x:
						guiSurface.blit(cobblestone_item, (guiSurface.get_width()//2-256+x["slot"]*64+8, guiSurface.get_height()-64+8))
						text = fonts[16].render(str(x["amount"]), config["enableAntialiasing"]["font"], (255, 255,255))
						guiSurface.blit(text, (guiSurface.get_width()//2-256+x["slot"]*64+32, guiSurface.get_height()-64+32))


		pygame.draw.rect(guiSurface, (255, 0, 0), (guiSurface.get_width()//2-256+player.selectedSlot*64, guiSurface.get_height()-64, 64, 64), 3)

		if inventoryGuiOpened:
			guiSurface.blit(inventoryGui, inventoryGui_rect)
			guiSurface.blit(player.defaultNormal, (200, 200))
			for rect in range(len(inventoryRects)):
				if rect <= 63:
					guiSurface.blit(inventoryCell, inventoryRects[rect])
				else:
					if rect <= 71:
						guiSurface.blit(inventoryHotbar, inventoryRects[rect])
					else:
						if rect == 75:
							guiSurface.blit(inventoryCell_green, inventoryRects[rect])
						else:
							guiSurface.blit(inventoryCell, inventoryRects[rect])
			for x in inventoryItems:
				x.render()
			for rect in inventoryRects:
				if rect.collidepoint(pygame.mouse.get_pos()):
					itemSlotHover = pygame.Surface((160//inventoryScaleIndex, 160//inventoryScaleIndex))
					itemSlotHover.set_alpha(85)
					itemSlotHover.convert_alpha()
					itemSlotHover.fill((255, 255, 255))
					guiSurface.blit(itemSlotHover, rect)
		
		if paused == "main":
			guiSurface.blit(pauseMenu, (4,4))
			resume.render()
			settings.render()
			exit.render()
		elif paused == "settings":
			guiSurface.blit(pauseMenu, (4,4))
			guiSurface.blit(fullscreenTitle, fullscreenTitle_rect)
			guiSurface.blit(gpuAccelerationTitle, gpuAccelerationTitle_rect)
			guiSurface.blit(showAnimationsTitle, showAnimationsTitle_rect)
			guiSurface.blit(antialiasTitle, antialiasTitle_rect)
			guiSurface.blit(fontAntialiasTitle, fontAntialiasTitle_rect)
			guiSurface.blit(guiAntialiasTitle, guiAntialiasTitle_rect)
			guiSurface.blit(textureAntialiasTitle, textureAntialiasTitle_rect)
			fullscreen.render(guiSurface)
			gpuAcceleration.render(guiSurface)
			showAnimations.render(guiSurface)
			fontAntialias.render(guiSurface)
			guiAntialias.render(guiSurface)
			textureAntialias.render(guiSurface)
			apply.render()
			back.render()

		# for x in player.inventory:
		# 	if "slot" in x:
		# 		if player.selectedSlot == x["slot"]:
		# 			if x["item"] == GUN:
		# 				guiSurface.blit(gunCursor, (pygame.mouse.get_pos()[0]-32, pygame.mouse.get_pos()[1]-32))
		# 		else:
		
		guiSurface.blit(cursor, pygame.mouse.get_pos())

		fpsCount = fonts[20].render("FPS: "+str(int(clock.get_fps())), config["enableAntialiasing"]["font"], (255, 255, 255))
		guiSurface.blit(fpsCount, (10, 10))
		if config["smartRender"]:
			renderRect = pygame.Rect(player.newRect.centerx-screen.get_width()//2, player.newRect.centery-screen.get_height()//2, screen.get_width(), screen.get_height())
		else:
			renderRect = pygame.Rect(player.newRect.centerx-config["renderDistance"]*32, player.newRect.centery-config["renderDistance"]*32, config["renderDistance"]*64, config["renderDistance"]*64)
		# pygame.draw.rect(gameSurface, (255, 0, 0), renderRect, 3)
		screen.blit(gameSurface, gameSurface_Rect)
		screen.blit(guiSurface, (0,0))


		pygame.display.update()
soundtrack1 = pygame.mixer.music.load(os.path.join(musicPath, "soundtrack1.ogg"))
pygame.mixer.music.play()
menu()