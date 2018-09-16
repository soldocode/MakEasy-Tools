# -*- coding: utf-8 -*-
"""
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
        self.appendToolbar("MeTools", ["MeFaceToDXF"])
        self.appendMenu("MeTools", ["MeFaceToDXF"])
        Log ("Loading MakEasy Module... done\n")

    def Activated(self):
                # do something here if needed...
         Msg ("MeWorkbench.Activated()\n")

    def Deactivated(self):
                # do something here if needed...
         Msg ("MeWorkbench.Deactivated()\n")

FreeCADGui.addWorkbench(MakEasyWorkbench)
