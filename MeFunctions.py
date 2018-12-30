"""
@author: Riccardo Soldini
"""

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
    print 'angle between faces:',alpha
    return alpha


def angle_to_Z(face):
    vns1 = FreeCAD.Vector(0,0,1)
    vns2 = face.normalAt(0,0)
    alpha = math.degrees( vns1.getAngle( vns2 ) )
    print 'angle between faces:',alpha
    return alpha


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


def find_adjacent(faces,first):
    group=[first]
    contacts={}
    count_adjacents=0
    while len(group)>0:
        #print 'group:', group
        index_face=group.pop(0)
        if not index_face in contacts:
            contacts[index_face]={}
            e1=faces[index_face].OuterWire.Edges
            for index_compare in range(0,len(faces)):
                if index_compare!=index_face:
                    e2=faces[index_compare].OuterWire.Edges
                    for geo1 in range(0,len(e1)):
                        for geo2 in range(0,len(e2)):
                            if e1[geo1].isSame(e2[geo2]):
                                count_adjacents+=1
                                contacts[index_face][geo1]=[index_compare,geo2]
                                if index_compare not in group:group.append(index_compare)

    print len(contacts),' linked faces found:'
    pp.pprint(contacts)
    return contacts


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
