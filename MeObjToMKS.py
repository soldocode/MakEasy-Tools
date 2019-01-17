# -*- coding: utf-8 -*-
"""
@author: Riccardo Soldini
"""

import FreeCAD,FreeCADGui,Part
import sys
import pprint
sys.path.append(u"C:\SOLDINISNC\PyApp\mystuff")
sys.path.append(u"C:\SOLDINISNC\PyApp\makEasy")
sys.path.append(u"C:\\Users\\UFFICIO TECNICO\\Anaconda3\\lib\\site-packages")
sys.path.append(u"\PyApp\mystuff")
sys.path.append(u"\PyApp\makEasy")
sys.path.append(u"C:\\Users\\Disegno\\Anaconda3\\lib\\site-packages")
import makEasy,g2
from PySide import QtGui
from MeFunctions import *

fac=[]
POSSIBLE_THK=[2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0,12.0,15.0,20.0,25.0,30.0,35.0,40.0]
POSSIBLE_UNP=[40,50,60,65,80,100,120,140,160,180,180,200,220,240,300]
COMMON_COMP={'RIDUZIONE_CONCENTRICA_114_76':{'name':'Riduzione concentrica D114-76'},
             'ROSETTA_DIN7980_d_10':{'name':'Rosetta piana d10'},
             'VITE_UNI5739_M10x30':{'name':'Vite TE M10x30'},
             '3572_BB14_00':{'name':'Profilo a U 28x14 L=200'},
             'p9.1.1.1.1.1.1':{'name':'Piastrina fissatubo'},
             'S400-1102D':{'name':'Piastrina fissatubo'},
             'supporto.1.1.1.1':{'name':'Supporto ripari L=20'},
             'supporto.1.2.1.1':{'name':'Supporto ripari L=40'},
             'S300-1191A_00.1':{'name':'Piastrina supporto ripari L=40'},
             'S300-1191A_00.2':{'name':'Piastrina supporto ripari L=20'},
             'S300-1126B':{'name':'Blocchetti 30x20x10 filettati'}}

class MeObjToMKS_Tool:
    "MeObjToMKS tool object"


    def GetResources(self):
        return {"MenuText": "Estrai Oggetti",
                "ToolTip": "Crea oggetti makeEasy da selezione",
                "Pixmap"  :""
               }

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        else:
            return True

    def Activated(self):
        PARTS={}
        print ("Let's begin...")
        pp = pprint.PrettyPrinter(indent=4)
        sels=FreeCADGui.Selection.getSelectionEx()
        count=0
        for sel in sels:
            obj=sel.Object
            if hasattr(obj,"Shape"):
                if obj.Shape.Volume>0:
                    print ("Object ", obj.Label)
                    count+=1
                    part_name=deconstruct_object(obj)
                    if part_name in PARTS:
                        PARTS[part_name]['count']+=1
                        PARTS[part_name]['objects'].append(obj.Label)
                    else:
                        PARTS[part_name]={'count':1,'objects':[obj.Label]}
        print ('Rilevati nr ',count,' oggetti')
        pp.pprint(PARTS)

        for item in PARTS:
            print (item+'  |  '+str(PARTS[item]['count']))
        print('... all done!')

        return


def deconstruct_object(obj):
        part_name='indefinito'
        comcomp=False
        for c in COMMON_COMP:
            if c in obj.Label:
                part_name=COMMON_COMP[c]['name']
                comcomp=True
        if not comcomp:
            faces=obj.Shape.Faces

            c_surf={}
            p_surf={}
            b_part=[]
            plane_areas={}
            faces_areas={}
            faces_tree={"Plane":{},
                        "Cylinder":{},
                        "Cone":{}}

            fnum=len(faces)
            print ('Number of faces:',fnum)

            ### create color tree
            actcolor=obj.ViewObject.DiffuseColor[0]
            dcol=[]
            for i in range (0,fnum):
                dcol.append(actcolor)

            ### Build faces's tree
            for i in range(0,len(faces)):
                area=faces[i].Area
                if area in faces_areas:
                    faces_areas[area].append(i)
                else:
                    faces_areas[area]=[i]

                str_face=faces[i].Surface.__str__()
                if str_face=="<Cylinder object>":
                    #print ("Cylinder",i," - center:",faces[i].Surface.Center)
                    c_surf[i]=faces[i]
                    faces_tree['Cylinder'][i]=faces[i]
                elif str_face=="<Plane object>":
                    #print ("Plane",i," - number of edges:",len(faces[i].Edges))
                    p_surf[i]=faces[i]
                    faces_tree['Plane'][i]=faces[i]
                    area=faces[i].Area
                    if area in plane_areas:
                        plane_areas[area].append(i)
                    else:
                        plane_areas[area]=[i]
                elif str_face=="<Cone object>":
                    #print ("Cone",i," - center",faces[i].Surface.Center)
                    faces_tree['Cone'][i]=faces[i]

            ### Find greater faces
            eight_top_areas=sorted(faces_areas,reverse=True)[:8]
            #print (eight_top_areas)
            eight_bigger_faces=[]
            count=0
            index=0
            while (count<8) and (index<len(eight_top_areas)):
                #print 'f:',faces_areas[eight_top_areas[index]]
                for i in range (0,len(faces_areas[eight_top_areas[index]])):
                    eight_bigger_faces.append(faces_areas[eight_top_areas[index]][i])
                    count+=1
                index+=1
            #print 'ebf',eight_bigger_faces
            classified=False

            ##### is it round tube? #####
            curved_faces=True
            group=list(eight_bigger_faces)
            for i in range(0,4):
                if group[i] not in faces_tree['Cylinder']:
                    curved_faces=False

            if curved_faces:
                dd=[]
                for n in range (0,4):
                    nn=eight_bigger_faces[n]
                    for m in range (0,4):
                        mm=eight_bigger_faces[m]
                        dist=round(faces_tree['Cylinder'][mm].distToShape(faces_tree['Cylinder'][nn])[0],2)
                        if dist not in dd: dd.append(dist)
                if len(dd)==2:
                    dd.remove(0)
                    diam=0
                    lenght=0
                    for i in range (0,4):
                        ff=faces_tree['Cylinder'][eight_bigger_faces[i]]
                        d=ff.Surface.Radius*2
                        if d>diam:diam=d
                        edges=ff.OuterWire.Edges
                        for e in edges:
                            if str(e.Curve.__class__)=="<type 'Part.GeomLineSegment'>":
                                if e.Length>lenght:lenght=e.Length

                    part_name= "Tubo tondo diam."+str(diam)+"x"+str(dd[0])+" L="+str(lenght)
                    classified=True

            four_faces=[]
            two_faces=[]
            pface_count=0
            if not classified:
                group=[]
                #print faces_tree['Plane'].keys()
                #print eight_bigger_faces
                for g in list(eight_bigger_faces):
                    if g in faces_tree['Plane'].keys():
                        pface_count+=1
                        group.append(g)
                #print 'gr',group
                while len(group)>0:
                    sample=group.pop(0)
                    #print sample
                    matched=[]
                    matched_count=1
                    for i in group:
                        #print i
                        if is_planes_parallels(faces_tree['Plane'][sample],faces_tree['Plane'][i]):
                            matched_count+=1
                            matched.append(i)
                    matched.append(sample)
                    #print  matched_count
                    if matched_count==4:
                        #print "4 parallels faces found:",matched
                        four_faces.append(matched)
                    if matched_count==2:
                        #print "2 parallels faces found:",matched
                        two_faces.append(matched)

                ##### is it a rect/square tube? #####
                if len(four_faces)==2:
                    classified=True
                    size1=int(max_faces_distance(list(four_faces[0]),faces_tree['Plane']))
                    size2=int(max_faces_distance(list(four_faces[1]),faces_tree['Plane']))
                    thk=min_faces_distance(list(four_faces[0]),faces_tree['Plane'])
                    lenght=max_found_len(list(four_faces[0]),faces_tree['Plane'])
                    if size1==size2:
                        part_name= "Tubo quadro "+str(size1)+"x"+str(thk)+" L="+str(lenght)
                    elif size1>size2:
                        part_name= "Tubo rettangolare "+str(size1)+"x"+str(size2)+"x"+str(thk)+" L="+str(lenght)
                    else:
                        part_name= "Tubo rettangolare "+str(size2)+"x"+str(size1)+"x"+str(thk)+" L="+str(lenght)
                ##### is it a UNP profile? #####
                elif len(two_faces)==2:
                    size1=int(max_faces_distance(list(two_faces[0]),faces_tree['Plane']))
                    size2=int(max_faces_distance(list(two_faces[1]),faces_tree['Plane']))
                    lenght=max_found_len(list(two_faces[0]),faces_tree['Plane'])
                    #print size1
                    if size1>size2 and size1 in POSSIBLE_UNP:
                        classifed=True
                        part_name= "UNP "+str(size1)+" L="+str(lenght)
                    elif size2 in POSSIBLE_UNP:
                        classifed=True
                        part_name= "UNP "+str(size2)+" L="+str(lenght)


            ### find thickness
            if not classified:
                same_geometry=False
                group=list(eight_bigger_faces)

                if (group[0] in faces_tree['Plane']) and (group[1] in faces_tree['Plane']):
                    f1=faces_tree['Plane'][group[0]]
                    f2=faces_tree['Plane'][group[1]]
                    same_geometry=True

                if (group[0] in faces_tree['Cylinder']) and (group[1] in faces_tree['Cylinder']):
                    f1=faces_tree['Cylinder'][group[0]]
                    f2=faces_tree['Cylinder'][group[1]]
                    same_geometry=True

                if same_geometry:
                    thk=round(f1.distToShape(f2)[0],1)
                    print ('thk: ',thk)

                    if thk in POSSIBLE_THK:
                        part_name= 'Sagoma sp. '+str(thk)+' mm'

                    weight=round(obj.Shape.Volume*0.0000079,1)
                    part_name+=' ('+str(weight)+'kg)'

                    c_surf=list(faces_tree['Cylinder'])
                    nblend=0
                    blend_faces=[]
                    #print c_surf
                    while len(c_surf)>0:
                        s1=c_surf.pop(0)
                        not_found=True
                        ind=0
                        while ind<len(c_surf) and not_found:
                            c1=faces_tree['Cylinder'][s1]
                            c2=faces_tree['Cylinder'][c_surf[ind]]
                            blend_thk=c1.Surface.Radius-c2.Surface.Radius
                            #print 'bt ',blend_thk
                            cc1=c1.Surface.Center
                            cc2=c2.Surface.Center
                            eqX=round(cc1.x, 2)==round(cc2.x, 2)
                            eqY=round(cc1.y, 2)==round(cc2.y, 2)
                            eqZ=round(cc1.z, 2)==round(cc2.z, 2)
                            equal_center= (eqX and eqY) or (eqX and eqZ) or (eqZ and eqY)
                            if (equal_center) and (abs(blend_thk)==thk):
                                nblend+=1
                                not_found=False
                                print ('blend faces...: ',s1,' and ',c_surf[ind])
                                blend_faces.append(s1)
                                blend_faces.append(c_surf[ind])
                            ind+=1
                    if nblend==1: part_name+=" con nr "+str(nblend)+" piega"
                    if nblend>1: part_name+=" con nr "+str(nblend)+" pieghe"
                    if nblend>0:
                        #print 'find adjacent...maybe..',eight_bigger_faces
                        contacts=find_adjacent(faces,eight_bigger_faces[0])
                        adc=contacts[eight_bigger_faces[0]]
                        print ('adc:',adc)
                        if eight_bigger_faces[0] in faces_tree['Plane']:
                            for b in blend_faces:
                                for ad in adc:
                                    if b==adc[ad][0]:
                                        print (' Trovato!!!' ,adc[ad])
                                        f1=faces[eight_bigger_faces[0]]
                                        f2=faces[adc[ad][0]]
                                        e1= f1.OuterWire.Edges[ad]
                                        e2= f2.OuterWire.Edges[adc[ad][1]]
                                        fac.append(e1)
                                        fac.append(e2)
                                        fp=e1.Curve.StartPoint
                                        ep=e1.Curve.EndPoint
                                        dx=round(fp.x-ep.x,3)
                                        dy=round(fp.y-ep.y,3)
                                        dz=round(fp.z-ep.z,3)
                                        a=angle_between_planes(f1,f2)
                                        print (angle_to_Z(f1))
                                        print ('deltas:',dx,'|',dy,'|',dz,'->',a)
                        #fac.append(faces[eight_bigger_faces[0]])

        return part_name
