# -*- coding: utf-8 -*-
from game import *

FONT_NAME = "freesansbold.ttf"

#Button options
BUTTON_TEXTSIZE = 24
BUTTON_BACKCOLOR = (190,190,190)
BUTTON_HOVERCOLOR = (220,220,220)
BUTTON_TEXTCOLOR = (0,0,0)
BUTTON_MARGIN = 6
BUTTON_OPACITY = 160

#Menu options
MENU_BACKCOLOR = (200,200,200)
MENU_OPACITY = 50
MENU_MARGIN = 10
MENU_TITLESIZE = 32
MENU_TITLECOLOR = (220,220,220)

CHECK_BACKCOLOR = (0,0,0)
CHECK_OPACITY = 180
PRIZE_MARGIN = 120

TEXTBOX_TEXTSIZE = 24
TEXTBOX_BACKCOLOR = (60,60,60)
TEXTBOX_HOVERCOLOR = (80,80,80)
TEXTBOX_TEXTCOLOR = (255,255,255)
TEXTBOX_MARGIN = 6
TEXTBOX_OPACITY = 180

CURSOR_FLASH_TICKS = 250

PRIZE_TEXTSIZE = 64
PRIZE_TEXTCOLOR = (150 , 255, 100)

UNSEEN_BALL_ALPHA = 60

class GUIComponent:
    """Defines a GUI component. Every element in the GUI must inherit from
    this class.

    parent -> The parent component, or None"""
    def __init__(self,parent = None):
        self.parent= parent
        if parent: parent.addChild(self)
        self.rect = Rect(0,0,0,0)

    def setPosition(self,x,y):
        self.rect.x = x
        self.rect.y = y

    def setSize(self,w,h):
        self.rect.w = w
        self.rect.h = h

    def move(self,xmove,ymove):
        self.rect = self.rect.move(xmove,ymove)

    def setRect(self, rect):
        self.rect = rect

    def getRect(self):
        return Rect(self.rect)

class GUIContainer(GUIComponent):
    """A GUI element that can contain other elements"""
    def __init__(self, parent = None):
        GUIComponent.__init__(self,parent)
        self.children = []

    def addChild(self,guicomponent):
        self.children.append(guicomponent)

    def setPosition(self,x,y):
        xdisp, ydisp = x-self.rect.x, y-self.rect.y
        GUIComponent.setPosition(self,x,y)
        for child in self.children:
            child.move(xdisp,ydisp)

    def move(self,xmove,ymove):
        GUIComponent.move(self,xmove,ymove)
        for child in self.children:
            child.move(xmove,ymove)

    def setRect(self, rect):
        xdisp, ydisp = rect.x-self.rect.x, rect.y-self.rect.y
        GUIComponent.setRect(self,rect)
        for child in self.children:
            child.move(xdisp,ydisp)



class Window(GameObject, GUIContainer):
    """A movible container, with frame and decoration"""
    def __init__(self, parent = None):
        GUIContainer.__init__(self, parent)

    def processEvent(self,event):
        for child in self.children:
            if not child.processEvent(event): return False
        return True

    def erase(self, surface):
        pass

    def paint(self, surface):
        for child in self.children:
            child.paint(surface)

class HotKeyManager(GameObject):
    """A GameObject that is binds key presses to actions"""
    def __init__(self,game, priority = 5):
        GameObject.__init__(self,game,priority)
        self.actions = []
        game.addEventListener(self)

    def addAction(self,key,action, interrupt_events = False):
        self.actions.append((key,action, interrupt_events))

    def processEvent(self,event):
        if event.type == KEYDOWN:
            for action in self.actions:
                if event.key == action[0]:
                    action[1](event)
                    return not action[2]

        return True

class TextButton(GameObject, GUIComponent):

    def __init__(self,game, text, action = None, priority = 10, depth = 10, width = 0, height = 0, parent = None):
        GameObject.__init__(self,game,priority,depth)
        GUIComponent.__init__(self, parent)

        self.hover = False
        self.action = action

        #Create font and text surface
        font = pygame.font.Font(FONT_NAME,BUTTON_TEXTSIZE)
        text = font.render(text,1,BUTTON_TEXTCOLOR)

        #Set width and height for the button, if specified, or use
        #text surface if not specified
        if width !=0: self.rect.w = width
        else: self.rect.w = text.get_rect().w + 2*BUTTON_MARGIN
        if height !=0: self.rect.h = height
        else : self.rect.h = text.get_rect().h + 2*BUTTON_MARGIN

        #Make normal and hovered surface
        self.surface_normal = pygame.Surface((self.rect.w,self.rect.h)).convert()
        self.surface_hover = self.surface_normal.copy()

        #Render background and text
        text_rect = text.get_rect()
        text_rect.centerx, text_rect.centery = self.rect.centerx, self.rect.centery
        self.surface_normal.set_alpha(BUTTON_OPACITY)
        self.surface_hover.set_alpha(BUTTON_OPACITY)
        self.surface_normal.fill(BUTTON_BACKCOLOR)
        self.surface_hover.fill(BUTTON_HOVERCOLOR)
        self.surface_normal.blit(text,text_rect)
        self.surface_hover.blit(text,text_rect)

    def paint(self, surface):
        if self.hover:
            surface.blit(self.surface_hover,self.rect)
        else:
            surface.blit(self.surface_normal,self.rect)

    def processEvent(self, event):
        if event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos): self.hover = True
            else: self.hover = False
        elif self.hover and event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.action != None: self.action()

        return True

class TextBox(GameObject, GUIComponent):

    def __init__(self,game, text, priority = 10, depth = 10, width = 100, height = 0, numeric=False, onenter = None, parent = None):
        GameObject.__init__(self,game,priority,depth)
        GUIComponent.__init__(self, parent)

        self.hover = False
        self.height = height
        self.numeric = numeric

        #Set width and height for the button, if specified, or use
        #text surface if not specified
        self.rect.w = width

        self.font = pygame.font.Font(FONT_NAME,TEXTBOX_TEXTSIZE)
        text_surface = self.font.render("XXX",1,TEXTBOX_TEXTCOLOR)
        if self.height !=0: self.rect.h = self.height
        else : self.rect.h = text_surface.get_rect().h + 2*TEXTBOX_MARGIN

        #Make normal and hovered surface
        self.surface_normal = pygame.Surface((self.rect.w,self.rect.h)).convert()
        self.surface_normal.set_alpha(TEXTBOX_OPACITY)
        self.surface_hover = self.surface_normal.copy()
        self.surface_hover.set_alpha(TEXTBOX_OPACITY)

        self.cursor = self.font.render("|",1,TEXTBOX_TEXTCOLOR)

        self.surface_normal.fill(TEXTBOX_BACKCOLOR)
        self.surface_hover.fill(TEXTBOX_HOVERCOLOR)

        self.setText(text)
        self.ticks = pygame.time.get_ticks()
        self.paint_cursor = True
        self.onenter = onenter

    def setText(self, text):
        #Create text surface
        self.text = text

        self.text_surface = self.font.render(self.text,1,TEXTBOX_TEXTCOLOR)
        self.text_rect = self.text_surface.get_rect()

    def paint(self, surface):
        if self.hover:
            surface.blit(self.surface_hover,self.rect)
        else:
            surface.blit(self.surface_normal,self.rect)

        self.text_rect.left = self.rect.left + TEXTBOX_MARGIN
        self.text_rect.centery = self.rect.top + self.surface_normal.get_rect().centery
        surface.blit(self.text_surface, self.text_rect)

        if pygame.time.get_ticks() - self.ticks > CURSOR_FLASH_TICKS:
            self.paint_cursor = not self.paint_cursor
            self.ticks = pygame.time.get_ticks()
        if self.paint_cursor:
            self.text_rect.left += self.text_rect.w
            surface.blit(self.cursor, self.text_rect)

    def processEvent(self, event):
        if event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos): self.hover = True
            else: self.hover = False
        if event.type == KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.setText(self.text[:-1])
                return False
            if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                self.setText(self.text + chr(event.key))
                return False
            #TO-DO: Improve, upper case, etc.
            if not self.numeric and event.key >= pygame.K_a and event.key <= pygame.K_z:
                self.setText(self.text + chr(event.key))
                return False
            if event.key == pygame.K_RETURN and self.onenter:
                self.onenter(self)

        return True

class Menu(Window):

    def __init__(self, game, width, parent = None, title=None):
        GameObject.__init__(self,game, 10)
        Window.__init__(self, parent)
        self.buttons = []
        self.title_text = title
        self.title_surf = None

        self.setSize(width,MENU_MARGIN)

        if self.title_text:
            font = pygame.font.Font(FONT_NAME,MENU_TITLESIZE)
            self.title_surf = font.render(self.title_text,1,MENU_TITLECOLOR)
            r = self.getRect()
            r.h = r.h + self.title_surf.get_rect().h + MENU_MARGIN
            self.setRect(r)


        self.__make_surface()

    def __make_surface(self):
        self.surface = pygame.Surface((self.rect.w,self.rect.h)).convert()
        self.surface.fill(MENU_BACKCOLOR)
        self.surface.set_alpha(MENU_OPACITY)

        ypos = self.rect.top + MENU_MARGIN
        if self.title_surf:
            ypos = ypos + MENU_MARGIN + self.title_surf.get_rect().h
        for button in self.buttons:
            button.setPosition(self.rect.left + MENU_MARGIN,ypos)
            ypos += button.rect.h + MENU_MARGIN

    def addOption(self, option_title, option_action):
        button = TextButton(self.game,
            text=option_title,
            action = option_action,
            width = self.rect.w - 2*MENU_MARGIN,
            depth = self.depth-1,
            parent = self)
        self.buttons.append(button)

        button.setPosition(MENU_MARGIN,self.rect.y+MENU_MARGIN)

        center = self.rect.center
        self.rect.h = self.rect.h + button.rect.h + MENU_MARGIN
        self.rect.center = center

        self.__make_surface()

    def paint(self, surface):
        surface.blit(self.surface,self.rect)
        if self.title_surf:
            r = self.title_surf.get_rect()
            r.centerx = self.rect.centerx
            r.top = self.rect.top + MENU_MARGIN
            surface.blit(self.title_surf,r)

        Window.paint(self,surface)

    def erase(self):
        self.game.restoreRect(self.rect)

class CheckCardWindow(Window):

    def __init__(self, game, width):
        GameObject.__init__(self,game, 50, 5)
        Window.__init__(self, None)
        self.title_text = "Comprobar Carton"
        self.title_surf = None

        self.setSize(width,MENU_MARGIN)

        font = pygame.font.Font(FONT_NAME,MENU_TITLESIZE)
        self.title_surf = font.render(self.title_text,1,MENU_TITLECOLOR)
        r = self.getRect()

        ypos = MENU_MARGIN + self.title_surf.get_rect().h + MENU_MARGIN

        def enter_pressed(textbox):
            self.bingo_prize = False
            self.line_prize = False
            self.checkCard(textbox.text)

        self.card_number = TextBox(self.game,
            text="",
            width=self.rect.w - 2*MENU_MARGIN,
            depth=self.depth-1,
            numeric = True,
            onenter = enter_pressed,
            parent = self)

        self.card_number.setPosition(self.rect.left + MENU_MARGIN, ypos)
        ypos += self.card_number.rect.h + MENU_MARGIN

        font = pygame.font.Font(FONT_NAME,PRIZE_TEXTSIZE)
        self.bingo_surf = font.render("BINGO!!!!!",1,PRIZE_TEXTCOLOR)
        self.line_surf = font.render("LINEA!",1,PRIZE_TEXTCOLOR)

        self.prize_top = ypos

        ypos += self.bingo_surf.get_rect().h + MENU_MARGIN

        self.back_button = TextButton(self.game,
            text="Volver",
            action = self.back,
            width = self.rect.w - 2*MENU_MARGIN,
            depth = self.depth-1,
            parent = self)

        self.back_button.setPosition(self.rect.left + MENU_MARGIN, ypos)
        ypos += self.back_button.rect.h + MENU_MARGIN

        self.bingo_prize = False
        self.line_prize = False

        r.h += ypos
        self.setRect(r)
        self.__make_surface()

    def __make_surface(self):
        self.surface = pygame.Surface((self.rect.w,self.rect.h)).convert()
        self.surface.fill(CHECK_BACKCOLOR)
        self.surface.set_alpha(CHECK_OPACITY)

    def paint(self, surface):
        surface.blit(self.surface,self.rect)
        r = self.title_surf.get_rect()
        r.centerx = self.rect.centerx
        r.top = self.rect.top + MENU_MARGIN
        surface.blit(self.title_surf,r)

        if self.bingo_prize:
            r = self.bingo_surf.get_rect()
            r.top = self.rect.top + self.prize_top
            r.centerx = self.rect.centerx
            surface.blit(self.bingo_surf, r)

        if self.line_prize:
            r = self.line_surf.get_rect()
            r.top = self.rect.top + self.prize_top
            r.centerx = self.rect.centerx
            surface.blit(self.line_surf, r)

        Window.paint(self,surface)

    def back(self):
        pass

    def erase(self):
        self.game.restoreRect(self.rect)

    def displayBingo(self):
        self.bingo_prize = True

    def displayLine(self):
        self.line_prize = True
