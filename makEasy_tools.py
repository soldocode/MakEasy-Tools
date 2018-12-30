# -*- coding: utf-8 -*-
"""

@author: Riccardo Soldini
"""

import FreeCADGui
#import sys
#sys.path.append(u"C:\SOLDINISNC\PyApp\mystuff")
#sys.path.append(u"C:\SOLDINISNC\PyApp\makEasy")
#sys.path.append(u"C:\\Users\\UFFICIO TECNICO\\Anaconda3\\lib\\site-packages")
#sys.path.append(u"\PyApp\mystuff")
#sys.path.append(u"\PyApp\makEasy")
#sys.path.append(u"C:\\Users\\Disegno\\Anaconda3\\lib\\site-packages")
#import makEasy,g2,math
#from PySide import QtGui

from MeFaceToDXF import *
from MeObjToMKS import *


FreeCADGui.addCommand('MeFaceToDXF',MeFaceToDXF_Tool())
FreeCADGui.addCommand('MeObjToMKS',MeObjToMKS_Tool())
