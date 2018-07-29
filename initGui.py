# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 22:44:09 2018

@author: Riccardo Soldini
"""

class MakEasyWorkbench ( Workbench ):
    "MakEasy workbench object"
    Icon = """
             /* XPM */
             static const char *test_icon[]={
             "16 16 2 1",
             "a c #000000",
             ". c None",
             "................",
             "................",
             "..############..",
             "..############..",
             "..############..",
             "......####......",
             "......####......",
             "......####......",
             "......####......",
             "......####......",
             "......####......",
             "......####......",
             "......####......",
             "......####......",
             "................",
             "................"};
           """
    MenuText = "MakEasy Tools"
    ToolTip = "workbench for MakEasy App"
 
    def GetClassName(self):
        return "Gui::PythonWorkbench"
     
    def Initialize(self):
        import tools
        self.appendToolbar("My Tools", ["MyCommand1"])
        self.appendMenu("My Tools", ["MyCommand1"])
        Log ("Loading MyModule... done\n")
 
    def Activated(self):
                # do something here if needed...
         Msg ("MyWorkbench.Activated()\n")
 
    def Deactivated(self):
                # do something here if needed...
         Msg ("MyWorkbench.Deactivated()\n")
 
FreeCADGui.addWorkbench(MakEasyWorkbench)