# -*- coding: utf-8 -*-
"""

@author: Riccardo Soldini
"""

import FreeCAD,FreeCADGui,Part
import sys
sys.path.append(u"C:\SOLDINISNC\PyApp\mystuff")
sys.path.append(u"C:\SOLDINISNC\PyApp\makEasy")
sys.path.append(u"C:\\Users\\UFFICIO TECNICO\\Anaconda3\\lib\\site-packages")
sys.path.append(u"\PyApp\mystuff")
sys.path.append(u"\PyApp\makEasy")
sys.path.append(u"C:\\Users\\Disegno\\Anaconda3\\lib\\site-packages")
import makEasy,g2,math
from PySide import QtGui


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

        def indexNode(x,y):
            i=0
            notfound=True
            while (notfound) and i<len(nodes):
                if (x==nodes[i][0]) and (y==nodes[i][1]):
                    notfound=False
                    i=i-1
                i=i+1
            if notfound:
                nodes.append([x,y])
                all_nodes.append(g2.Point(x,y))
            return i

        def createPaths(path,node,geos):
            while len(geos)>0:
                geo=geos.pop()
                if (geo[1]==node):
                    path.append(geo)
                    createPaths(path,geo[2],geos)
                elif (geo[2]==node):
                    path.append(geo)
                    createPaths(path,geo[1],geos)
            return dict(path=path,node=node,geos=geos)

        # create a copy of the selected face
        sel=FreeCADGui.Selection.getSelectionEx()[0]
        face=sel.SubObjects[0]
        obj=sel.Object
        copy_face = Part.Face(face.Wires)

        # align face on Z plane
        vns1 = face.normalAt(0.0,0.0)
        print 'Face normal vect: ',vns1.normalize(),'...'
        zdeg=vns1.getAngle(FreeCAD.Vector(0.0,0.0,1.0))
        print '...Rotation degree to Z plane: ',math.degrees(zdeg),'...'
        rAxis=FreeCAD.Rotation(FreeCAD.Vector(0.0,0.0,1.0),vns1.normalize()).Axis
        rDegree=-math.degrees(zdeg)
        rCenter=face.CenterOfMass
        face=copy_face
        face.Placement=FreeCAD.Placement(FreeCAD.Vector(0.0,0.0,0.0),
                                         FreeCAD.Rotation(rAxis,rDegree),
                                         rCenter).multiply(face.Placement)

        # find all paths
        edges=face.Edges
        nodes=[]
        paths=[]
        geos=[]
        all_nodes=[]
        all_geos=[]
        chains=[]
        for edge in edges:
            ind_nd=0
            type_edge=type(edge.Curve).__name__
            vertexes=edge.Vertexes
            if type_edge=='GeomLineSegment':
                txt='line'
                n1=indexNode(vertexes[0].X,vertexes[0].Y)
                n2=indexNode(vertexes[1].X,vertexes[1].Y)
                geos.append(['Line',n1,n2])
            elif type_edge=='GeomCircle':
                if len(edge.Vertexes)==1:
                    txt='circle'
                    n1=indexNode(edge.Curve.Center.x,edge.Curve.Center.y)
                    n2=indexNode(vertexes[0].X,vertexes[0].Y)
                    geos.append(['Circle',n1,n2])
                if len(edge.Vertexes)==2:
                        txt='arc'
                        n1=indexNode(vertexes[0].X,vertexes[0].Y)
                        n3=indexNode(vertexes[1].X,vertexes[1].Y)
                        mdldgr=edge.ParameterRange[0]+(edge.ParameterRange[1]-edge.ParameterRange[0])/2
                        middle=edge.valueAt(mdldgr)
                        n2=indexNode(middle.x,middle.y)
                        geos.append(['Arc',n1,n2,n3])
            elif type_edge=="GeomEllipse":
                txt='ellipse'
                n1=indexNode(vertexes[0].X,vertexes[0].Y)
                n2=indexNode(vertexes[1].X,vertexes[1].Y)
                f1=e.Curve.Focus1
                rM=e.Curve.MajorRadius
                rm=e.Curve.MinorRadius
                #geos.append(['Ellipse',n1,n2,f1,f2,rM])????
        while len(geos)>0:
            empty_search=False
            trovato=False
            act=geos.pop()
            chain=[act[1],act[0]]
            if act[0]=='Arc':
                chain.append(act[2])
            chain.append(act[-1])
            node_to_find=act[-1]
            while not empty_search:
                i=0
                empty_search=True
                while i<len(geos):
                    if geos[i][1]==node_to_find:
                        trovato=True
                        chain.append(geos[i][0])
                        if geos[i][0]=='Arc':
                            chain.append(geos[i][2])
                        chain.append(geos[i][-1])
                        node_to_find=geos[i][-1]
                    elif geos[i][-1]==node_to_find:
                        trovato=True
                        chain.append(geos[i][0])
                        if geos[i][0]=='Arc':
                            chain.append(geos[i][2])
                        chain.append(geos[i][1])
                        node_to_find=geos[i][1]
                    if trovato:
                        empty_search=False
                        act=geos[i]
                        geos.pop(i)
                        trovato=False
                    else:
                        i=i+1
            chains.append(chain)

        print('...',len(chains),' chains found ...')

        ### create a drawing
        dr=g2.Drawing()
        p_int=[]
        conta=0
        for c in chains:
            print(c)
            path=g2.Path(all_nodes,c)
            for i in range(0,len(path.geometries)):
                g=path.geo(i)
                print(g)
                dr.insertGeo(conta,g)
                conta+=1
        output_dxf=dr.getDXF()
        filename=QtGui.QFileDialog.getSaveFileName(None,"Salva DXF", "", ".DXF")
        f=open(filename[0],"w")
        f.write(output_dxf)
        f.close()

        print('... all done!')
        return
