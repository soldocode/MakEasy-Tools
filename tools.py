# -*- coding: utf-8 -*-
"""
Created on Sun Jul 29 09:22:21 2018

@author: Disegno
"""

import FreeCAD,FreeCADGui
 
class MyTool:
    "My tool object"

    def GetResources(self):
        return {"MenuText": "My Command",
                "Accel": "Ctrl+M",
                "ToolTip": "My extraordinary command",
                "Pixmap"  :""
               }
 
    def IsActive(self):
                if FreeCAD.ActiveDocument == None:
                        return False
                else:
                        return True
 
    def Activated(self):
        return
 
FreeCADGui.addCommand('MyCommand1',MyTool())
