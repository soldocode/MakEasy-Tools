
### MeFreeCADClasses.py
### 2020

from MeFunctions import *

class FCTreeSheet(object):
    def __init__(self,fc_object=None):
        self.FCObject=fc_object
        self.Root=None

class TSPlane(object):
    def __init__(self):
        self.PlaneUp=None
        self.PlaneDown=None
        self.Nodes={}

class TSBlend(object):
    def __init__(self):
        self.BlendUp=None
        self.BlendDown=None
        self.Nodes={}
