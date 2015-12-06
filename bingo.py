#!/usr/bin/python

from game import *
from gamegui import *
from ConfigParser import SafeConfigParser
import sys
import random
import os

CONFIG='bingo.cfg'

def configDefaults():
	global DELAY_NEXTBALL, BALL_SHOWTIME, USE_FULLSCREEN
	loadConfig()

	#Default config
	DELAY_NEXTBALL = getConfigInt('game','ball_delay',4000)
	BALL_SHOWTIME = getConfigInt('game','ball_showtime',DELAY_NEXTBALL - 1000)
	USE_FULLSCREEN = getConfigBool('display','fullscreen',False)


EVENT_BALL = USEREVENT
EVENT_LASTBALL = USEREVENT+1
NUM_BOLAS = 90

BALL_TEXTSIZE = 200
BALL_TEXTCOLOR = (1,1,1)
BALL_SMALLSIZE = (45,45)
BALL_BIGSIZE = (200,200)
BALL_MARGIN = 10
BALL_STEPS = 15

PENDING_TEXTSIZE = 50
PENDING_TEXTCOLOR = (200,200,200)

#1 PauseScreen (solo acepta P para quitarla)
#5 HotkeyManager

SCREEN_RES = (800,600)
STATE_MAINMENU, STATE_PLAYING, STATE_PAUSED, STATE_FINISHED, STATE_OPTIONS = range(5)

def loadConfig():
	global config
	config = SafeConfigParser()
	try:
		config.readfp(file(CONFIG))
	except Exception, e:
		pass
	
def getConfigBool(section,key,default):
	try:
		return config.getboolean(section,key)
	except:
		setConfig(section,key,default)
		return default
	
def getConfigInt(section,key,default):
	try:
		return config.getint(section,key)
	except:
		setConfig(section,key,default)
		return default
	
def setConfig(section,key,value):
	if not config.has_section(section):
		config.add_section(section)
	config.set(section,key,str(value))
	
def saveConfig():
	config.write(file(CONFIG,"w"))

def exitGame():
	saveConfig()
	sys.exit(0)

def startGame():
	game.setState(STATE_PLAYING)
	BingoRound(game)

def options():
	game.setState(STATE_OPTIONS)
	OptionsMenu(game)


def toggleFullScreen(ev):
	setConfig('display','fullscreen',game.toggleFullscreen())
	return False

def escapeKey(ev):
	if game.getState() == STATE_PLAYING:
		game.setState(STATE_PAUSED)
		PauseMenu(game)
	elif game.getState() == STATE_PAUSED:
		game.setState(STATE_PLAYING)
	elif game.getState() == STATE_MAINMENU:
		exitGame()
	elif game.getState() == STATE_FINISHED:
		game.setState(STATE_MAINMENU)

	return False

def loadImage(name):
	fullname = os.path.join('data',name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemEXit, message
	return image.convert()

def loadSound(name):
	class NoneSound:
		def play(self): pass
		def get_length(self): return 0
	if not pygame.mixer:
		return NoneSound()
	fullname = os.path.join('data',name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print  'Cannot load sound:', name, message
		return NoneSound()
		raise SystemExit, message
	return sound

class Title(GameObject):
	
	def __init__(self,game):
		GameObject.__init__(self,game)
		
		self.title = loadImage('title.png')
		self.rect = self.title.get_rect()
		self.title.set_colorkey((0,0,0))
		self.rect.centerx = SCREEN_RES[0]/2
		self.rect.top = 20
		self.game.addPainter(self)
		
		self.title_small = pygame.transform.scale(self.title,(200,50))
		self.rect_small = self.title_small.get_rect()
		self.rect_small.top = 20
		self.rect_small.centerx = 110

		
	def paint(self,surface):
		if self.game.getState() in (STATE_MAINMENU, STATE_OPTIONS):
			surface.blit(self.title,self.rect)
		else:
			surface.blit(self.title_small,self.rect_small)

class PauseMenu(Menu):
	
	def __init__(self,game):
		Menu.__init__(self,game,200, title="PAUSA")

		self.addOption("Reanudar",self.resumeGame)
		self.addOption("Salir",self.toMainMenu)

		self.setDepth(10)
		#TODO: Make this work, be it before or after addOptions
		r=self.getRect()
		r.left = BALL_MARGIN
		r.bottom = SCREEN_RES[1] - BALL_MARGIN
		self.setRect(r)

		self.game.addPainter(self)
		self.game.addEventListener(self)
		
	def stateChanged(self,state):
		if state in (STATE_MAINMENU, STATE_PLAYING):
			self.game.removeObject(self)
			
	def toMainMenu(self):
		self.game.setState(STATE_MAINMENU)
		
	def resumeGame(self):
		self.game.setState(STATE_PLAYING)
		
	def processEvent(self, event):
		if event.type == KEYDOWN and event.key == K_SPACE:
			game.setState(STATE_PLAYING)
		Menu.processEvent(self,event)
		return True
		

class StartMenu(Menu):
	
	def __init__(self, game):
		Menu.__init__(self,game,SCREEN_RES[0]/2, title="MENU PRINCIPAL")

		self.addOption("Comenzar partida",startGame)
		self.addOption("Opciones",options)
		self.addOption("Salir",exitGame)
		self.game.addPainter(self)
		self.game.addEventListener(self)				

		r = self.getRect()
		r.centerx, r.centery=SCREEN_RES[0]/2 , SCREEN_RES[1]/2
		self.setRect(r)
		
	def stateChanged(self,state):
		self.game.removeObject(self)


class ShowTimeMenu(Menu):
	
	def __init__(self, game):
		Menu.__init__(self,game,SCREEN_RES[0]/2, title="TIEMPO DE BOLA")

		for i in (1,2,3,4,5,6):
			if getConfigInt('game','ball_showtime',BALL_SHOWTIME) == i * 1000:
				self.addOption("[ " + str(i) + " segundos ]",self.setDelay(i*1000))
			else:
				self.addOption(str(i) + " segundos",self.setDelay(i*1000))
		self.addOption("Volver",self.back)
		self.game.addPainter(self)
		self.game.addEventListener(self)				

		r = self.getRect()
		r.centerx, r.top=SCREEN_RES[0]/2 , 175
		self.setRect(r)
		
	def back(self):
		self.game.removeObject(self)
		OptionsMenu(game)
		
	def setDelay(self,value):
		return lambda: self.setDelayReal(value)

	def setDelayReal(self,value):
		global BALL_SHOWTIME
		BALL_SHOWTIME = value
		setConfig('game','ball_showtime',str(value))
		self.game.removeObject(self)
		ShowTimeMenu(self.game)

class DelayMenu(Menu):
	
	def __init__(self, game):
		Menu.__init__(self,game,SCREEN_RES[0]/2, title="TIEMPO ENTRE BOLAS")

		if getConfigInt('game','ball_delay',DELAY_NEXTBALL) == 0:
			self.addOption("[ Manual ]",self.setDelay(0))
		else:
			self.addOption("Manual",self.setDelay(0))
		for i in (2,3,4,5,7,10):
			if getConfigInt('game','ball_delay',DELAY_NEXTBALL) == i * 1000:
				self.addOption("[ " + str(i) + " segundos ]",self.setDelay(i*1000))
			else:
				self.addOption(str(i) + " segundos",self.setDelay(i*1000))
		self.addOption("Volver",self.back)
		self.game.addPainter(self)
		self.game.addEventListener(self)				

		r = self.getRect()
		r.centerx, r.top=SCREEN_RES[0]/2 , 175
		self.setRect(r)
		
	def back(self):
		self.game.removeObject(self)
		OptionsMenu(game)
		
	def setDelay(self,value):
		return lambda: self.setDelayReal(value)

	def setDelayReal(self,value):
		global DELAY_NEXTBALL		
		DELAY_NEXTBALL = value
		setConfig('game','ball_delay',str(value))
		self.game.removeObject(self)
		DelayMenu(self.game)

class OptionsMenu(Menu):
	
	def __init__(self, game):
		Menu.__init__(self,game,SCREEN_RES[0]/2, title="OPCIONES")

		self.addOption("Tiempo entre bolas",self.setDelay)
		self.addOption("Tiempo de bola",self.setShowTime)		
		self.addOption("Pantalla Completa",self.toggleFullScreen)
		self.addOption("Volver",self.mainmenu)
		self.game.addPainter(self)
		self.game.addEventListener(self)				

		r = self.getRect()
		r.centerx, r.centery=SCREEN_RES[0]/2 , SCREEN_RES[1]/2
		self.setRect(r)
	
	def setDelay(self):
		self.game.removeObject(self)
		DelayMenu(game)
		
	def setShowTime(self):
		self.game.removeObject(self)
		ShowTimeMenu(game)
	
	def mainmenu(self):
		self.game.setState(STATE_MAINMENU)
		StartMenu(game)
		
	def stateChanged(self,state):
		self.game.removeObject(self)
			
	def toggleFullScreen(self):
		toggleFullScreen(None)


class Round:
	"""A Bingo round. Function 'ball' will take a random ball, and return it."""
	def __init__(self):
		self.pending_balls = range(1,NUM_BOLAS+1)
		self.seen_balls = []

	def pendingBalls(self):
		return self.pending_balls

	def ball(self):
		if not self.pending_balls:
			return None
		next_ball = random.choice(self.pending_balls)
		self.pending_balls.remove(next_ball)
		self.seen_balls.append(next_ball)
		return next_ball

class BallPainter(GameObject):
	
	ball_surface = None
	UNSEEN, SEEN, CURRENT, MOVING = range(4)
	
	def __init__(self,game,ballnum):
		GameObject.__init__(self,game)
		game.addPainter(self)
		self.number = ballnum
		
		if not BallPainter.ball_surface:
			BallPainter.ball_surface = loadImage('ball.png')
			BallPainter.ball_surface.set_colorkey((0,0,0))
		
		self.state = BallPainter.UNSEEN
		self.surface_big = BallPainter.ball_surface.copy()
		
		#Create font and text surface
		font = pygame.font.Font(None,BALL_TEXTSIZE)
		text = font.render(str(ballnum),1,BALL_TEXTCOLOR)
		
		self.rect = self.surface_big.get_rect()
		text_rect = text.get_rect()
		text_rect.centerx, text_rect.centery = self.rect.centerx, self.rect.centery
		self.surface_big.blit(text,text_rect)
		
		self.surface = pygame.transform.scale(self.surface_big,BALL_SMALLSIZE)
		self.rect = self.surface.get_rect()
		self.rect.centerx, self.rect.centery = self.ballPosition(ballnum)
		self.surface.set_alpha(15)
	
	def ballPosition(self,ball):
		x = SCREEN_RES[0] - ((9-(ball-1)) % 10) * (BALL_SMALLSIZE[0] + BALL_MARGIN) - BALL_SMALLSIZE[0] - BALL_MARGIN
		y = BALL_SMALLSIZE[1] + ((ball-1) / 10) * (BALL_SMALLSIZE[1] + BALL_MARGIN) 
		return (x,y)
			
	def paint(self, surface):
		surface.blit(self.surface,self.rect)		
		if self.state in (BallPainter.CURRENT, BallPainter.MOVING):
			surface.blit(self.surface_curr,self.rect_curr)			
		
	def seen(self):
		self.state = BallPainter.CURRENT		
		
		self.setDepth(self.depth - 1)
		
		self.surface_curr = pygame.transform.scale(self.surface_big,BALL_BIGSIZE)
		self.rect_curr = self.surface.get_rect()
		self.rect_curr.top, self.rect_curr.left = 150 + BALL_MARGIN, BALL_MARGIN 
		self.surface_curr.set_alpha(255)
		self.ticks = pygame.time.get_ticks()
		
	def update(self):
		if self.state == BallPainter.CURRENT:
			if pygame.time.get_ticks() - self.ticks > BALL_SHOWTIME:
				self.state = BallPainter.MOVING
				self.move_step = 0
		elif self.state == BallPainter.MOVING:

			curr_w = BALL_SMALLSIZE[0] + (BALL_STEPS - self.move_step) * (BALL_BIGSIZE[0] - BALL_SMALLSIZE[0])/ BALL_STEPS
			curr_h = BALL_SMALLSIZE[1] + (BALL_STEPS - self.move_step) * (BALL_BIGSIZE[1] - BALL_SMALLSIZE[1])/ BALL_STEPS
			
			self.surface_curr = pygame.transform.scale(self.surface_big,(curr_w,curr_h))
			self.rect_curr = self.surface.get_rect()
			self.rect_curr.top = 150 + BALL_MARGIN + self.move_step * (self.rect.top - self.rect_curr.top - 150 ) / BALL_STEPS
			self.rect_curr.left = BALL_MARGIN + self.move_step * (self.rect.left - self.rect_curr.left) / BALL_STEPS
			self.ticks = pygame.time.get_ticks()
			
			self.move_step = self.move_step + 1
			if self.move_step > BALL_STEPS:
				self.surface.set_alpha(255)
				self.state = BallPainter.SEEN
				self.setDepth(self.depth + 1)
				
	def clear(self):
		game.removeObject(self)



class BingoRound(GameObject):
	def __init__(self,game):
		GameObject.__init__(self,game)
		
		game.addEventListener(self)
		game.addPainter(self)
		
		self.round = Round()
		self.played_balls = []
		self.last_ball = None
		self.smallball = loadImage('smallball.png')
		self.smallball.set_colorkey((0,0,0))

		self.pendingfont = pygame.font.Font(None,PENDING_TEXTSIZE)

		self.ball_painters = []
		for i in range(1,NUM_BOLAS+1):
			self.ball_painters.append(BallPainter(game,i))
		
		sound_begin = loadSound('begin.ogg')
		sound_begin.play()
		
		pygame.mouse.set_visible(False)
		
		if DELAY_NEXTBALL > 0:
			pygame.time.set_timer(EVENT_BALL,DELAY_NEXTBALL + int(sound_begin.get_length() * 1000))
		
		
	def paint(self,surface):

		rect = self.smallball.get_rect()
		bolitas = len(self.round.pendingBalls())
		played_balls = len(self.played_balls)
		if bolitas > 30: bolitas = 30
		for i in range(bolitas):
			rect.centerx = random.randint(0,200)
			rect.centery = SCREEN_RES[1] - random.expovariate(9) * 100
			surface.blit(self.smallball,rect)
			
		
		self.pendingtext = self.pendingfont.render("BOLAS JUGADAS: " + str(played_balls),1,PENDING_TEXTCOLOR)
		rect = self.pendingtext.get_rect()
		rect.centery = 550
		rect.centerx = 500
		surface.blit(self.pendingtext,rect)
	
	def processEvent(self,event):
		if event.type == MOUSEBUTTONDOWN:
			if self.game.getState() == STATE_PLAYING and DELAY_NEXTBALL:
				game.setState(STATE_PAUSED)
				PauseMenu(game)
			elif self.game.getState() == STATE_PLAYING:
				pygame.event.post(pygame.event.Event(EVENT_BALL))
			elif self.game.getState() == STATE_FINISHED:
				game.setState(STATE_MAINMENU)
		elif event.type == KEYDOWN and event.key == K_SPACE:
			game.setState(STATE_PAUSED)
			PauseMenu(game)
		elif event.type == KEYDOWN and event.key == K_RETURN:
			pygame.time.set_timer(EVENT_BALL,0)
			pygame.event.post(pygame.event.Event(EVENT_BALL))			
		elif event.type == EVENT_BALL:

			ball = self.round.ball()
			self.last_ball = ball
			
			if not ball:
				pygame.time.set_timer(EVENT_BALL,0)
				game.setState(STATE_FINISHED)
				sound = loadSound("end.ogg")
				sound.play()
				return True
			
			self.ball_painters[ball-1].seen()
			self.played_balls.append(ball)
			

			sound = loadSound(str(ball) + '.ogg')
			sound.play()
			
			if DELAY_NEXTBALL > 0:
				pygame.time.set_timer(EVENT_BALL,DELAY_NEXTBALL+int(sound.get_length()*1000))
			
		elif event.type == EVENT_LASTBALL:
			pygame.time.set_timer(EVENT_LASTBALL,0)
			
			if self.last_ball:
				self.ball_painters[self.last_ball-1].seen()

				sound = loadSound(str(self.last_ball) + '.ogg')
				sound.play()

				if DELAY_NEXTBALL > 0:
					pygame.time.set_timer(EVENT_BALL,DELAY_NEXTBALL+int(sound.get_length()*1000))

			else:
				pygame.time.set_timer(EVENT_BALL,DELAY_NEXTBALL)
				
		return True
		
		
	def stateChanged(self,state):
		if state == STATE_MAINMENU:
			pygame.mouse.set_visible(True)
			StartMenu(self.game)
			#Title(self.game)
			for ball in self.ball_painters:
				ball.clear()
			game.removeObject(self)
		elif state == STATE_PLAYING:
			pygame.mouse.set_visible(False)
			game.addEventListener(self)
			game.addPainter(self)
			
			#Reproducir "Continua el juego", y esperar su duracion y repetir ultima bola
			sound = loadSound('resume.ogg')
			sound.play()	
			pygame.time.wait(500 + int(sound.get_length() * 1000))
			
			if self.last_ball:
				sound = loadSound('lastball.ogg')
				sound.play()
				pygame.time.wait(500 + int(sound.get_length() * 1000))
			
			pygame.event.post(pygame.event.Event(EVENT_LASTBALL))
		elif state == STATE_PAUSED:
			pygame.mouse.set_visible(True)
			game.removeEventListener(self)
			game.removePainter(self)
			pygame.time.set_timer(EVENT_BALL,0)
			pygame.time.set_timer(EVENT_LASTBALL,0)
			sound = loadSound('pause.ogg')
			sound.play()			

configDefaults()

game = Game(SCREEN_RES,"Bingo AIM",100, fullscreen = USE_FULLSCREEN) 

hotkeys = HotKeyManager(game)
hotkeys.addAction(K_ESCAPE,escapeKey,True)
hotkeys.addAction(K_f,toggleFullScreen,True)

back = loadImage('back.jpg')

game.background.blit(back,(0,0))

game.setState(STATE_MAINMENU)

StartMenu(game)
Title(game)

game.mainLoop()
