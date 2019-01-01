import sys
from PySide import QtGui ,QtCore
app = QtGui.qApp
mw = FreeCADGui.getMainWindow()

for child in mw.children():
   print 'widget name = ', child.objectName(), ', widget type = ', child
