# CS3388B
# Kohei Yasui
# March 14th, 2022
# This class creates a light source object to show light onto an image.
import numpy as np
from matrix import matrix

class lightSource:
    # constructor for light
    def __init__(self,position=matrix(np.zeros((4,1))),color=(0,0,0),intensity=(1.0,1.0,1.0)):
        self.__position = position
        self.__color = color
        self.__intensity = intensity

    # getter for position
    def getPosition(self):
        return self.__position

    # getter for color
    def getColor(self):
        return self.__color

    # getter for intensity
    def getIntensity(self):
        return self.__intensity

    # setter for position
    def setPosition(self,position):
        self.__position = position

    # setter for color
    def setColor(self,color):
        self.__color = color

    # setter for intensity
    def setIntensity(self,intensity):
        self.__intensity = intensity
