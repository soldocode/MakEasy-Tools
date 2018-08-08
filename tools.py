# -*- coding: utf-8 -*-
"""
Created on Sun Jul 29 09:22:21 2018

@author: Disegno
"""

import FreeCAD,FreeCADGui
 
class MeFaceToDXF_Tool:
    "MeFaceToDXF tool object"

    def GetResources(self):
        return {"MenuText": "Faccia->DXF",
                "ToolTip": "Crea DXF da una faccia",
                "Pixmap"  :""
               }
 
    def IsActive(self):
                if FreeCAD.ActiveDocument == None:
                        return False
                else:
                        return True
 
    def Activated(self):
        print('il comando funziona di brutto')
        return
 
FreeCADGui.addCommand('MeFaceToDXF',MeFaceToDXF_Tool())
