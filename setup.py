from distutils.core import setup
from modulefinder import Module
import py2exe
import pygame
import os

#NOTES: Copy freesansbold.ttf to dist/
#NOTES: Copy pygame DLLS to dist/
#NOTES: Copy data to dist/
#NOTES: Copy cards.csv to dist/


setup(windows=[{
    "script": 'bingo.py',
    "icon_resources": [(0, "bingo.ico")] 
    }],
      options={
          "py2exe": {
              "excludes": ["OpenGL.GL", "Numeric", "copyreg", "itertools.imap", "numpy", "pkg_resources", "queue", "winreg", "pygame.SRCALPHA", "pygame.sdlmain_osx"],
              }
          }
      )
