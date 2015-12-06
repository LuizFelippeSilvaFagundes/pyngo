import pygame
from pygame.locals import *
import sys

class GameObject:
    """Represents anything that interacts in the gaming. It may be painted or not, it may
    respond to events or not, create another GameObjects, etc"""
    
    def __init__(self,game, priority=50, depth=50):
        """Init the GameObject instance, adding it to a Game instance"""
        self.game = game
        self.priority = priority
        self.depth = depth

        game.addObject(self)
        
    def getPriority(self):
        """Returns the GameObject instance priority"""
        return self.priority

    def getDepth(self):
        """Returns the GameObject instance depth (for painting)"""
        return self.depth
    
    def setPriority(self, priority):
        self.priority = priority
        if self.game: self.game.sortPriority()

    def setDepth(self, depth):
        self.depth = depth
        if self.game: self.game.sortDepth()


    def erase(self):
        return True
    
    def paint(self, surface):
        return True
    
    def processEvent(self,event):
        return True
    
    def update(self):
        return True
    
    def stateChanged(self,state):
        pass


class Game:
    
    def __init__(self, screen_res, game_title = "", fps = 0, fullscreen = False):
        """Create a new Game instance, starting SDL/pygame with the desired
        screen resolution
        
        screen_res -> (width,height)
        game_title -> Game title
        game_ticks (default=0) -> Ticks after every frame
        """
        
        #List of game objects
        self.game_objects  = []
        #List of event listener  (sorted by priority)
        self.event_listeners = []
        #List of game objects (sorted by paint order)
        self.paint_list = []
            
        #Initialize pygame
        pygame.init()
        pygame.display.set_caption(game_title)

        #Check modules
        if not pygame.font:
            print 'Cannot load Font module'
            raise SystemExit

        #Get first available display mode
        self.fullscreen = fullscreen
        self.screen = pygame.display.set_mode(screen_res, fullscreen and FULLSCREEN or 0)
        
        #Create the background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        #Create a clock object, for timing
        self.clock = pygame.time.Clock()		
        self.fps = fps
        
        self.state = None
    
    def setState(self, state):
        self.state = state
        for gobj in self.game_objects:
            gobj.stateChanged(state)
            
    def toggleFullscreen(self):
        self.fullscreen = not self.fullscreen
        screen_res = self.screen.get_rect().w, self.screen.get_rect().h
        self.screen = pygame.display.set_mode(screen_res, self.fullscreen and FULLSCREEN or 0)
        return self.fullscreen
            
    def getState(self):
        return self.state
    
    def restoreRect(self,rect):
        self.screen.blit(self.background,(0,0))

        
    def addObject(self,game_object):
        """Add a GameObject to the game objects collection. This will make the object
        aware of painting, erasing, update events, as well as input or user events
        
        game_object -> the GameObject instance to add
        """
        #Add object to event and paint list
        self.game_objects.append(game_object)
        
    def addEventListener(self, game_object):
        if game_object not in self.event_listeners:
            self.event_listeners.append(game_object)
            self.sortPriority()
        
    def removeEventListener(self, game_object):
        if game_object in self.event_listeners:
            self.event_listeners.remove(game_object)
        
    def addPainter(self, game_object):
        if game_object not in self.paint_list:
            self.paint_list.append(game_object)
            self.sortDepth()

    def removePainter(self, game_object):
        if game_object in self.paint_list:
            self.paint_list.remove(game_object)

    def removeObject(self, game_object):
        self.game_objects.remove(game_object)
        if game_object in self.paint_list: self.paint_list.remove(game_object)
        if game_object in self.event_listeners: self.event_listeners.remove(game_object)

    def sortPriority(self):    
        #Sort by priority
        self.game_objects.sort(lambda x,y: x.getPriority() < y.getPriority() and -1 or 1)
        
    def sortDepth(self):
        self.paint_list.sort(lambda x,y: x.getDepth() < y.getDepth() and 1 or -1)
        
    def mainLoop(self):
        """Start the main game loop"""
        self.screen.blit(self.background,(0,0))
                
        while True:

            for gobj in self.paint_list:
                gobj.paint(self.screen)
            
            #Update screen
            pygame.display.flip()
        
            #Update objects
            for gobj in self.game_objects:
                gobj.update()

            #Post events to all game_objects
            for event in pygame.event.get():
                if event.type == QUIT: sys.exit()
                for gobj in self.event_listeners:
                    if not gobj.processEvent(event): break

            for gobj in self.paint_list:
                gobj.erase()
                
            #Previous one will just mark rectangles for erasing. Now
            #do the real erasing, copying from the background
            self.screen.blit(self.background,(0,0))
            
        
            #If time is temporized	
            if self.fps != 0:
                self.clock.tick(self.fps)
                
        def setFlag(self,flag,vale):
            self.flags[flag] = value
            
        def getFlag(self,flag):
            return set.flags[flag]
            
