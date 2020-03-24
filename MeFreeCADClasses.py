
### MeFreeCADClasses.py
### 2020

from MeFunctions import *

class FCTreeSheet(object):
    def __init__(self,fc_object=None):
        self.FCObject=fc_object
        self.Root=None
        self.parse()

    def parse(self):
        print ('eccomi')

class Branch(object):
    def __init__(self,Class='Plane',Angle=0):
        self.FCTreeSheet=None
        self.Joints=[]
        self.Class=Class # could be Plane or Blend
        self.Angle=Angle
        self.FaceUp=None
        self.FaceDown=None

class Joint(object):
    def __init__(self):
        self.Status='free'
        self.FromBranch=None
        self.ToBranch=None
        self.JoinUP=[0,0,0] #[GeoIdFrom,FaceIdTo,GeoIdTo]
        self.JoinDown=[0,0,0] #[GeoIdFrom,FaceIdTo,GeoIdTo]
