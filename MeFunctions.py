"""
@author: Riccardo Soldini
"""

import math,pprint
import FreeCAD,Part
import g2
import makEasy
from FreeCAD import Placement,Rotation

POSSIBLE_THK=[1.0,1.5,2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0,12.0,15.0,20.0,25.0,30.0,35.0,40.0]

class FCObject(object):
    def __init__(self,FCObj=None,):
        self.FCObj=FCObj
        self.Faces={}
        self.Weight=round(FCObj.Shape.Volume*0.0000079,1)
        self.PartName='indefinito'
        self.Classified=False
        self.meItem=None

    def parse(self):
        self.Faces=self.FCObj.Shape.Faces
        self.FacesByArea=get_faces_by_area(self.Faces)
        self.FaceRoot=self.FacesByArea[sorted(self.FacesByArea,reverse=True)[:1][0]][0]
        self._getFacesMap()
        self._setEightBiggerFaces()
        self.FacesTree=build_faces_tree(self.Faces,self.FacesMap['Faces'])
        #self.FacesTree=build_faces_tree(self.FacesMap['Faces'])
        ### costruire facemap qui ???

    def _setEightBiggerFaces(self):
        self.EightBiggerFaces=[]
        eight_top_areas=sorted(self.FacesByArea,reverse=True)[:8]
        count=0
        index=0
        while (count<8) and (index<len(eight_top_areas)):
           for i in range (0,len(self.FacesByArea[eight_top_areas[index]])):
               self.EightBiggerFaces.append(self.FacesByArea[eight_top_areas[index]][i])
               count+=1
           index+=1

    def _getThickness(self):
        thk=0
        same_geometry=False
        group=list(self.EightBiggerFaces)

        if (group[0] in self.FacesTree['Plane']) and (group[1] in self.FacesTree['Plane']):
            f1=self.FacesTree['Plane'][group[0]]
            f2=self.FacesTree['Plane'][group[1]]
            same_geometry=True
        if (group[0] in self.FacesTree['Cylinder']) and (group[1] in self.FacesTree['Cylinder']):
            f1=self.FacesTree['Cylinder'][group[0]]
            f2=self.FacesTree['Cylinder'][group[1]]
            same_geometry=True

        if same_geometry:
            thk=round(f1.distToShape(f2)[0],1)

        if thk in POSSIBLE_THK:
            self.Thk=thk
            print('... thickness is ',self.Thk)

    def _getAnyBends(self):
        c_surf=list(self.FacesTree['Cylinder'])
        self.BendedFaces=[]
        self.NumberOfBend=0
        #bend_faces=[]
        while len(c_surf)>0:
            s1=c_surf.pop(0)
            not_found=True
            ind=0
            while ind<len(c_surf) and not_found:
                c1=self.FacesTree['Cylinder'][s1]
                c2=self.FacesTree['Cylinder'][c_surf[ind]]
                bend_thk=round(c1.distToShape(c2)[0],2)
                cc1=c1.Surface.Axis
                cc2=c2.Surface.Axis
                eqX=round(cc1.x, 2)==round(cc2.x, 2)
                eqY=round(cc1.y, 2)==round(cc2.y, 2)
                eqZ=round(cc1.z, 2)==round(cc2.z, 2)
                equal_center= (eqX and eqY) or (eqX and eqZ) or (eqZ and eqY)
                if (equal_center) and (abs(bend_thk)==self.Thk):
                    self.NumberOfBend+=1
                    not_found=False
                    self.BendedFaces.append([s1,c_surf[ind]])
                    #bend_faces.append(s1)
                    #bend_faces.append(c_surf[ind])
                ind+=1
        print('... found ',self.NumberOfBend,' bend')


    def _getFacesMap(self):
        self.FacesMap=faces_map(self.Faces,self.FaceRoot)


    def _isHProfile(self):
        result=False
        return result

    def _isRectTube(self):
        result=False
        return result

    def _isCommonComponent(self,comm_comp):
        result=False
        for c in comm_comp:
            if c in self.FCObj.Label:
              self.PartName=comm_comp[c]['name']
              self.Classified=True
              self.meItem=makEasy.Item(Id=self.PartName)
              result=True
        return result


def normalized_degrees(angle):
     accuracy=7
     a=math.degrees(round(angle,accuracy))
     n=a-int(a/360)*360
     if n<0:n=n+360
     return n


def angle_between_planes(face1,face2):
    vns1 = face1.normalAt(0,0)
    vns2 = face2.normalAt(0,0)
    alpha = math.degrees( vns1.getAngle( vns2 ) )
    print ('angle between faces:',alpha)
    return alpha


def align_face_to_Zplane(face):
    vns1 = FreeCAD.Vector(0,1,0)
    n=face.normalAt(0,0)
    if abs(n.z)!=1.0:
        vns2 = FreeCAD.Vector(n.x,n.y,0).normalize()
        alpha = math.degrees( vns1.getAngle( vns2 ))
        face.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),alpha)
        #print ('angle to YZ plane:',alpha)
    vns1 = FreeCAD.Vector(0,0,1)
    n=face.normalAt(0,0)
    if abs(n.x)!=1.0:
        vns2 = FreeCAD.Vector(0,n.y,n.z).normalize()
        alpha = math.degrees( vns1.getAngle( vns2 ))
        face.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0),alpha)
        #print ('angle to ZX plane:',alpha)
    return face


def angle_to_Z(face):
    vns1 = FreeCAD.Vector(0,0,1)
    vns2 = face.normalAt(0,0)
    alpha = math.degrees( vns1.getAngle( vns2 ))
    print ('angle to Z axis:',alpha)
    return round(alpha,6)


def angle_to_Y(face):
    vns1 = FreeCAD.Vector(0,1,0)
    vns2 = face.normalAt(0,0)
    alpha = math.degrees( vns1.getAngle( vns2 ))
    print ('angle to Y axis:',alpha)
    return round(alpha,6)


def angle_to_X(face):
    vns1 = FreeCAD.Vector(1,0,0)
    vns2 = face.normalAt(0,0)
    alpha = math.degrees( vns1.getAngle( vns2 ))
    print ('angle to X axis:',alpha)
    return round(alpha,6)


def is_edges_parallels(edge1,edge2):
    result=False
    d1=edge1.Curve.Direction
    d2=edge2.Curve.Direction
    print (d1)
    print (d2)
    if abs(d1.x)==abs(d2.x) and abs(d1.y)==abs(d2.y) and abs(d1.z)==abs(d2.z):
        print ('paralleli')
        result=True
    return result


def get_parallel_edges(face):
    e_list=[]
    for i in range(0,len(face.OuterWire.Edges)):
        found=False
        e=face.OuterWire.Edges[i]
        for c in e_list:
           if is_edges_parallels(e,face.OuterWire.Edges[c[0]]):
               c.append(i)
               found=True
        if not found:
            e_list.append([i])

    dist={}
    for pe in e_list:
        if len(pe)>1:
            e1=face.OuterWire.Edges[pe.pop(0)]
            p1=g2.Point(e1.Vertexes[0].X,e1.Vertexes[0].Y)
            p2=g2.Point(e1.Vertexes[1].X,e1.Vertexes[1].Y)
            l1=g2.Line(p1,p2)
            for e in pe:
                e2=face.OuterWire.Edges[e]
                p1=g2.Point(e2.Vertexes[0].X,e2.Vertexes[0].Y)
                p2=g2.Point(e2.Vertexes[1].X,e2.Vertexes[1].Y)
                l2=g2.Line(p1,p2)
                print(l1)
                print(l2)

    return dist


def get_box_dimensions(obj):
    bb=obj.Shape.BoundBox
    return [round(bb.XLength,2),round(bb.YLength,2),round(bb.ZLength,2)]


def get_faces_by_area(faces,scope=None):
   if scope==None: scope=[*range(0,len(faces))]
   faces_by_area={}
   for i in scope:
      area=faces[i].Area
      if area in faces_by_area:
          faces_by_area[area].append(i)
      else:
          faces_by_area[area]=[i]
   return faces_by_area


def build_faces_tree(faces,scope=None):
    if scope==None: scope=[*range(0,len(faces))]
    faces_tree={"Plane":{},
                "Cylinder":{},
                "Cone":{}}
    ### Build faces's tree
    for i in scope:
       str_face=faces[i].Surface.__str__()
       if str_face=="<Cylinder object>":
           faces_tree['Cylinder'][i]=faces[i]
       elif str_face=="<Plane object>":
           faces_tree['Plane'][i]=faces[i]
       elif str_face=="<Cone object>":
           faces_tree['Cone'][i]=faces[i]
    return faces_tree


def is_planes_parallels(face1,face2):

    def plane_from_3points(p1,p2,p3):

       M=[float(p2.X-p1.X),float(p2.Y-p1.Y),float(p2.Z-p1.Z),
          float(p3.X-p1.X),float(p3.Y-p1.Y),float(p3.Z-p1.Z)]
       K=[M[1]*M[5]-M[2]*M[4],
          M[2]*M[3]-M[0]*M[5],
          M[0]*M[4]-M[1]*M[3]]
       P=[K[0],K[1],K[2],-(K[0]*p1.X+K[1]*p1.Y+K[2]*p1.Z)]
       return P

    result=False
    v1=face1.OuterWire.Vertexes
    p1=plane_from_3points(v1[0],v1[1],v1[2])

    v2=face2.OuterWire.Vertexes
    p2=plane_from_3points(v2[0],v2[1],v2[2])

    n=p1[0]*p2[0]+p1[1]*p2[1]+p1[2]*p2[2]
    sq1=math.sqrt(p1[0]**2+p1[1]**2+p1[2]**2)
    sq2=math.sqrt(p2[0]**2+p2[1]**2+p2[2]**2)
    if sq1*sq2!=0.0:
        cosP=n/(sq1*sq2)
    else:
        cosP=0
    #print 'cosP:',cosP
    if abs(cosP)==1: result=True

    return result


def faces_map(faces,root):
    #id_root=self.EightBiggerFaces[0]
    num_faces=len(faces)
    group=[root]
    map={}
    count_adjacents=0
    while len(group)>0:
        index_face=group.pop(0)
        if not index_face in map:
            map[index_face]={}
            e1=faces[index_face].OuterWire.Edges
            for index_compare in range(0,num_faces):
                if index_compare!=index_face:
                    e2=faces[index_compare].OuterWire.Edges
                    for geo1 in range(0,len(e1)):
                        for geo2 in range(0,len(e2)):
                            if e1[geo1].isSame(e2[geo2]):
                                count_adjacents+=1
                                map[index_face][geo1]=[index_compare,geo2]
                                if index_compare not in group:
                                    group.append(index_compare)

    print (len(map),' linked faces found:')
    return {'Root':root,'Map':map,'Faces':list(map.keys())}



def min_faces_distance(faces,planes):
    dist=1000.0
    while len(faces)>0:
        f=faces.pop()
        for i in faces:
            d=round(planes[f].distToShape(planes[i])[0],1)
            if d<dist:dist=d
    return dist


def max_faces_distance(faces,planes):
    dist=0
    while len(faces)>0:
        f=faces.pop()
        for i in faces:
            d=round(planes[f].distToShape(planes[i])[0],1)
            if d>dist:dist=d
    return dist


def max_found_len(faces,planes):
    l=0
    for f in faces:
        for e in planes[f].Edges:
         if e.Length>l:
             l=e.Length
    return round(l,0)


def min_found_len(faces,planes):
    l=1000000
    for f in faces:
        for e in planes[f].Edges:
         if e.Length<l:
             l=e.Length
    return round(l,2)


def geos_from_face(_face):

    def indexNode(x,y):
        i=0
        notfound=True
        while (notfound) and i<len(nodes):
            if (x==nodes[i].x) and (y==nodes[i].y):
                notfound=False
                i=i-1
            i=i+1
        if notfound:
            nodes.append(g2.Point(x,y))
        return i

    # create a copy of the selected face
    face = Part.Face(_face.Wires)
    align_face_to_Zplane(face)

    edges=face.Edges
    nodes=[]
    geos=[]
    for edge in edges:
        ind_nd=0
        type_edge=type(edge.Curve).__name__
        vertexes=edge.Vertexes
        if type_edge=='GeomLineSegment'or type_edge=='Line' :
            txt='line'
            n1=indexNode(vertexes[0].X,vertexes[0].Y)
            n2=indexNode(vertexes[1].X,vertexes[1].Y)
            geos.append(['Line',n1,n2])
        elif type_edge=='GeomCircle' or type_edge=='Circle':
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
    return dict(geos=geos,nodes=nodes)


def changeColor(object,scope,new_color):
	actual_color=object.ViewObject.DiffuseColor[0]
	num_faces=len(object.Shape.Faces)
	col_array=[actual_color]*num_faces

	for c in scope:
		col_array[c]=new_color

	object.ViewObject.DiffuseColor=col_array	


def face_to_g2Shape(face):
    shape=None #g2.Shape()
    return shape
